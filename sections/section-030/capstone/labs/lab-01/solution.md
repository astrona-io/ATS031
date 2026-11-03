---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Capstone: Secure Two Hosts With Traefik TLS Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-capstone-030)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-capstone-030" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Create the certificates and the Secrets

```sh
for name in probe scout; do
  openssl req -x509 -nodes -newkey rsa:2048 -days 30 -keyout $name.key -out $name.crt -subj "/CN=$name.example.test" -addext "subjectAltName=DNS:$name.example.test"
  kubectl -n starfleet create secret tls $name-tls --cert=$name.crt --key=$name.key
done
```

## Create and repair the Ingresses

Save the Ingress `probe` as `ingress-probe.yaml`, using the host `probe.example.test`, the Service `probe` and the Secret `probe-tls`. Save the repaired Ingress `scout` as `ingress-scout.yaml`, using the host `scout.example.test`, the Service `scout` (not `probe`) and the Secret `scout-tls`. Both use class `traefik` and these annotations:

```yaml
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    traefik.ingress.kubernetes.io/router.tls: 'true'
```

The `probe` Ingress looks like this:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: probe
  namespace: starfleet
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    traefik.ingress.kubernetes.io/router.tls: 'true'
spec:
  ingressClassName: traefik
  rules:
  - host: probe.example.test
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: probe
            port:
              number: 80
  tls:
  - hosts:
    - probe.example.test
    secretName: probe-tls
```

Apply both files with `kubectl apply -f`. For `scout`, change the host, Service and Secret names in the same shape, and the class from `nginx` to `traefik`.

## Set the TLS policy and the redirect

Save the policy as `dynamic.yaml`:

```yaml
tls:
  options:
    default:
      minVersion: VersionTLS13
      sniStrict: true
```

Save the redirect arguments as `traefik-redirect-patch.json`:

```json
[
  {"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--entryPoints.web.http.redirections.entryPoint.to=websecure"},
  {"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--entryPoints.web.http.redirections.entryPoint.scheme=https"}
]
```

Apply the ConfigMap first, then patch the Deployment. The patch starts a new pod, which reads the new policy:

```sh
kubectl -n ingress-system create configmap traefik-dynamic --from-file=dynamic.yaml --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ingress-system patch deployment traefik --type=json --patch-file traefik-redirect-patch.json
kubectl -n ingress-system rollout status deployment/traefik
```

## Verify

Open a port forward to both ports in a second terminal and test each host:

```sh
kubectl -n ingress-system port-forward service/traefik 8080:80 8443:443
curl -s --cacert probe.crt --resolve probe.example.test:8443:127.0.0.1 https://probe.example.test:8443/
curl -s --cacert scout.crt --resolve scout.example.test:8443:127.0.0.1 https://scout.example.test:8443/
curl -si -H 'Host: scout.example.test' http://127.0.0.1:8080/ | head -n 5
openssl s_client -connect 127.0.0.1:8443 -servername probe.example.test -tls1_2 </dev/null 2>&1 | grep -E 'alert|handshake failure'
```

Each HTTPS request prints the response of its own application, the HTTP request returns a redirect to an `https://` address and TLS 1.2 fails.
## Common pitfalls

> [!WARNING]
> - **Leaving the `scout` backend on `probe`.** The class and the Service are both wrong.
> - **One certificate for both hosts by mistake.** Each host serves its own certificate.
> - **Replacing the `args` list with a merge patch.** Use the JSON patch.
> - **Not waiting for the rollout.** Tests before it ends hit the old pod.

## Clean up

Destroy the lab cluster when you are done:

```sh
astrona destroy ats-031-capstone-030
```
