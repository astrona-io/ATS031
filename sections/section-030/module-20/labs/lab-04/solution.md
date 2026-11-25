---
exam_objectives:
- Properly set up Ingress with TLS
---
# Match Exact And Prefix Paths Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-02-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-02-04" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Write the Ingress

`Exact` matches only the identical path. `Prefix` matches the path and every path below it, element by element. Save this as `ingress-api.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api
  namespace: starfleet-031-030-02-04
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web
spec:
  ingressClassName: traefik
  rules:
  - host: api.local
    http:
      paths:
      - path: /healthz
        pathType: Exact
        backend:
          service:
            name: beacon
            port:
              number: 80
      - path: /v1
        pathType: Prefix
        backend:
          service:
            name: scout
            port:
              number: 80
```

Apply it:

```sh
kubectl apply -f ingress-api.yaml
```

## Test each path

Open a port forward in a second terminal, then print the status code and the answering application for each path:

```sh
kubectl -n ingress-system port-forward service/traefik 8080:80
for path in /healthz /healthz/deep /v1 /v1/ships/7 /v2 /; do
  printf '%s ' "$path"
  curl -s -w ' %{http_code}\n' -H 'Host: api.local' "http://127.0.0.1:8080$path" | tail -c 60
done
```

`/healthz` reaches `beacon`, `/v1` and `/v1/ships/7` reach `scout`, and the other paths get `404`.

## Common pitfalls

> [!WARNING]
> - **Using `Prefix` for the health check.** Then `/healthz/deep` also reaches `beacon`.
> - **Adding a catch-all path `/`.** Every unknown path would then reach a Service instead of getting `404`.
> - **Writing `/v1/` with a trailing slash.** The task asks for `/v1`, and the request `/v1` itself must match.

## Clean up

Destroy the lab cluster when you are done:

```sh
astrona destroy ats-031-lab-030-02-04
```
