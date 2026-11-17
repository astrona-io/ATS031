---
exam_objectives:
- Properly set up Ingress with TLS
---
# Publish A Service By Host Name Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-02-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-02-03" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Write the Ingress

Save this as `ingress-depot.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: depot
  namespace: starfleet-031-030-02-03
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web
spec:
  ingressClassName: traefik
  rules:
  - host: depot.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: depot
            port:
              number: 80
```

Apply it:

```sh
kubectl apply -f ingress-depot.yaml
```

## Test with the Host header

Open a port forward in a second terminal. A request to `127.0.0.1` carries the host `127.0.0.1`, so set the `Host` header that the rule matches:

```sh
kubectl -n ingress-system port-forward service/traefik 8080:80 8443:443
curl -s -H 'Host: depot.local' http://127.0.0.1:8080/manifest
curl -s -o /dev/null -w '%{http_code}\n' -H 'Host: other.local' http://127.0.0.1:8080/
curl -sk -o /dev/null -w '%{http_code}\n' --resolve depot.local:8443:127.0.0.1 https://depot.local:8443/
```

The first response starts with `app=depot path=/manifest`. The other two print `404`: the second host has no rule, and the route exists only on the `web` entrypoint. The option `-k` skips the certificate check here because this test only reads the status code.

## Common pitfalls

> [!WARNING]
> - **Testing without a `Host` header.** Traefik matches the host, so a request to the bare address gets `404`.
> - **Forgetting the entrypoint annotation.** Without it Traefik attaches the router to every entrypoint, including `websecure`.
> - **Using `Exact` for the path `/`.** Then only the root path matches and `/manifest` gets `404`.

## Clean up

Destroy the lab cluster when you are done:

```sh
astrona destroy ats-031-lab-030-02-03
```
