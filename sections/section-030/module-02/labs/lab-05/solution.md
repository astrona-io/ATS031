---
exam_objectives:
- Properly set up Ingress with TLS
---
# Find A Broken Route With The Traefik API Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-02-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-02-05" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Read the controller log

Traefik writes an error when it cannot turn an Ingress into a route:

```sh
kubectl -n ingress-system logs deployment/traefik --tail=30 | grep -i beacon
kubectl -n starfleet-031-030-02-05 get ingress beacon -o jsonpath='{.spec.rules[0].http.paths[0].backend.service.port}{"\n"}'
kubectl -n starfleet-031-030-02-05 get service beacon -o jsonpath='{.spec.ports[0].name} {.spec.ports[0].port}{"\n"}'
```

The log names the Ingress and the Service port. The Ingress asks for the port name `web`, but the Service port is named `http`, so Traefik skips the whole route.

## Fix the backend port

Save this as `ingress-beacon.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: beacon
  namespace: starfleet-031-030-02-05
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web
spec:
  ingressClassName: traefik
  rules:
  - host: beacon.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: beacon
            port:
              name: http
```

Apply it:

```sh
kubectl apply -f ingress-beacon.yaml
```

## Read the router from the API

Open a port forward to the API port and the web port in a second terminal. Then list the routers with their rules:

```sh
kubectl -n ingress-system port-forward service/traefik 9000:8080 8080:80
curl -s http://127.0.0.1:9000/api/http/routers | python3 -m json.tool | grep -E '"(name|rule)"'
curl -s -H 'Host: beacon.local' http://127.0.0.1:8080/
```

The router for the rule ``Host(`beacon.local`) && PathPrefix(`/`)`` has a name that ends in `@kubernetes`. The `curl` request now returns a line that starts with `app=beacon`.

## Record the router name

Copy the name from the API output into the ConfigMap. Replace `<ROUTER>` with the name that the API printed:

```sh
kubectl -n starfleet-031-030-02-05 create configmap route-evidence --from-literal=router='<ROUTER>'
```

## Common pitfalls

> [!WARNING]
> - **Reading only the Ingress.** The Ingress looks valid; the log and the API show that Traefik skipped it.
> - **Recording the name without `@kubernetes`.** The API name includes the provider, and the task asks for the exact name.
> - **Leaving `--api.insecure=true` on a shared cluster.** It exposes every route without authentication. It is enabled here only for this exercise.

## Clean up

Destroy the lab cluster when you are done:

```sh
astrona destroy ats-031-lab-030-02-05
```
