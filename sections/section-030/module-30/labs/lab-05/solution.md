---
exam_objectives:
- Properly set up Ingress with TLS
---
# Redirect HTTP To HTTPS And Add HSTS Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-03-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-03-05" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Add the HSTS middleware

The middleware lives in the dynamic configuration of the file provider. Keep the TLS option that is already there. Save this as `dynamic.yaml`:

```yaml
tls:
  options:
    default:
      minVersion: VersionTLS12
http:
  middlewares:
    hsts:
      headers:
        stsSeconds: 300
```

Apply it by replacing the ConfigMap from the file:

```sh
kubectl -n ingress-system create configmap traefik-dynamic --from-file=dynamic.yaml --dry-run=client -o yaml > configmap-traefik-dynamic.yaml
kubectl apply -f configmap-traefik-dynamic.yaml
```

## Attach the middleware to the route

Save this as `ingress-harbor.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: harbor
  namespace: starfleet-031-030-03-05
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    traefik.ingress.kubernetes.io/router.tls: 'true'
    traefik.ingress.kubernetes.io/router.middlewares: hsts@file
spec:
  ingressClassName: traefik
  rules:
  - host: harbor.example.test
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: harbor
            port:
              number: 80
  tls:
  - hosts:
    - harbor.example.test
    secretName: harbor-tls
```

Apply it:

```sh
kubectl apply -f ingress-harbor.yaml
```

## Redirect on the entrypoint

The `args` list is not merged by key, so append the two arguments with a JSON patch. Save this as `traefik-redirect-patch.json`:

```json
[
  {"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--entryPoints.web.http.redirections.entryPoint.to=websecure"},
  {"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--entryPoints.web.http.redirections.entryPoint.scheme=https"}
]
```

Apply it and wait for the new pod, which also reads the new dynamic configuration:

```sh
kubectl -n ingress-system patch deployment traefik --type=json --patch-file traefik-redirect-patch.json
kubectl -n ingress-system rollout status deployment/traefik
```

## Verify

Open a port forward in a second terminal. Then read the headers of a plain HTTP request and of an HTTPS request:

```sh
kubectl -n ingress-system port-forward service/traefik 8080:80 8443:443
curl -si -H 'Host: harbor.example.test' http://127.0.0.1:8080/cargo | head -n 3
kubectl -n starfleet-031-030-03-05 get secret harbor-tls -o jsonpath='{.data.tls\.crt}' | base64 --decode > harbor.crt
curl -si --cacert harbor.crt --resolve harbor.example.test:8443:127.0.0.1 https://harbor.example.test:8443/ | grep -i strict-transport
```

The first response is a permanent redirect whose `Location` starts with `https://harbor.example.test`. The second shows `Strict-Transport-Security: max-age=300`.

## Common pitfalls

> [!WARNING]
> - **Replacing the whole `args` list with a merge patch.** Use a JSON patch that appends items.
> - **Dropping the TLS option `default` when you add the middleware.** The ConfigMap holds one file; write the whole file again.
> - **Expecting the HSTS header over plain HTTP.** Traefik adds it only on the HTTPS route that uses the middleware.

## Clean up

Destroy the lab cluster when you are done:

```sh
astrona destroy ats-031-lab-030-03-05
```
