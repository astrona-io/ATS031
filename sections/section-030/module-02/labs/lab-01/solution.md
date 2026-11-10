---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Route Two Services From One Host Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-02-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Inspect the starting state

```sh
kubectl get ingressclass
kubectl -n starfleet-031-030-02-01 get service
kubectl -n starfleet-031-030-02-01 get ingress
```

The class `traefik` exists, both Services listen on port 80 and no Ingress is present.

## Create the Ingress

Save this as `ingress-fleet.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fleet
  namespace: starfleet-031-030-02-01
spec:
  ingressClassName: traefik
  rules:
  - host: fleet.local
    http:
      paths:
      - path: /probe
        pathType: Prefix
        backend:
          service:
            name: probe
            port:
              number: 80
      - path: /scout
        pathType: Prefix
        backend:
          service:
            name: scout
            port:
              number: 80
```

Apply it:

```sh
kubectl apply -f ingress-fleet.yaml
```

## Verify

Open a port forward in a second terminal and test the three paths with a `Host` header:

```sh
kubectl -n ingress-system port-forward service/traefik 8080:80
curl -s -H 'Host: fleet.local' http://127.0.0.1:8080/probe
curl -s -H 'Host: fleet.local' http://127.0.0.1:8080/scout
curl -s -o /dev/null -w '%{http_code}\n' -H 'Host: fleet.local' http://127.0.0.1:8080/other
```

The first two responses name `probe` and `scout`, and the last command prints `404`.
## Common pitfalls

> [!WARNING]
> - **Naming the container port.** The backend names the Service port, which is 80.
> - **Forgetting `ingressClassName`.** Without it, Traefik may not serve the Ingress.
> - **Testing without a Host header.** The rule matches only `fleet.local`.

## Clean up

Destroy the lab cluster when you are done:

```sh
astrona destroy ats-031-lab-030-02-01
```
