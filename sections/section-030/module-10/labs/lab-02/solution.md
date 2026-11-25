---
exam_objectives:
- Properly set up Ingress with TLS
---
# Fix An Ingress That Traefik Ignores Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-01-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-01-02" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Find the mistakes

Read the class and the backend of the Ingress, then compare them with the classes in the cluster and the ports of the Service:

```sh
kubectl -n starfleet-031-030-01-02 get ingress relay -o jsonpath='{.spec.ingressClassName} {.spec.rules[0].http.paths[0].backend.service.port.number}{"\n"}'
kubectl get ingressclass
kubectl -n starfleet-031-030-01-02 get service relay -o jsonpath='{.spec.ports[0].port}{"\n"}'
```

The Ingress names the class `nginx`, and no controller serves that class, so Traefik ignores the object. The backend port is 8080, which is the container port. An Ingress backend must name the Service port, which is 80.

## Fix the Ingress

Save this as `ingress-relay.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: relay
  namespace: starfleet-031-030-01-02
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web
spec:
  ingressClassName: traefik
  rules:
  - host: relay.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: relay
            port:
              number: 80
```

Apply it:

```sh
kubectl apply -f ingress-relay.yaml
```

Then check the result. Open a port forward in a second terminal and send one request with the right host and one with another host:

```sh
kubectl -n ingress-system port-forward service/traefik 8080:80
curl -s -H 'Host: relay.local' http://127.0.0.1:8080/
curl -s -o /dev/null -w '%{http_code}\n' -H 'Host: other.local' http://127.0.0.1:8080/
```

The first request returns a line that starts with `app=relay`. The second prints `404`.

## Common pitfalls

> [!WARNING]
> - **Using the container port as the backend port.** The Ingress backend names the Service port, here 80.
> - **Changing only one mistake.** With the wrong class, Traefik ignores the Ingress. With the wrong port, Traefik cannot build the route. Both must be fixed.
> - **Testing without a `Host` header.** Traefik matches the host name, so a request to `127.0.0.1` without the header gets `404`.

## Clean up

Destroy the lab cluster when you are done:

```sh
astrona destroy ats-031-lab-030-01-02
```
