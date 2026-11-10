---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Publish Scout Over HTTPS With Your Own Certificate Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-03-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Create the certificate and the Secret

```sh
openssl req -x509 -nodes -newkey rsa:2048 -days 30 -keyout scout.key -out scout.crt -subj "/CN=scout.example.test" -addext "subjectAltName=DNS:scout.example.test"
kubectl -n starfleet-031-030-03-01 create secret tls scout-tls --cert=scout.crt --key=scout.key
```

On macOS the system `openssl` may not support `-addext`. Use a current OpenSSL, for example one installed with a package manager.

## Create the Ingress

Save this as `ingress-scout.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: scout
  namespace: starfleet-031-030-03-01
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    traefik.ingress.kubernetes.io/router.tls: 'true'
spec:
  ingressClassName: traefik
  rules:
  - host: scout.example.test
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: scout
            port:
              number: 80
  tls:
  - hosts:
    - scout.example.test
    secretName: scout-tls
```

```sh
kubectl apply -f ingress-scout.yaml
```

## Verify

Open a port forward in a second terminal and verify with the certificate as the trusted file:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443
curl -s --cacert scout.crt --resolve scout.example.test:8443:127.0.0.1 https://scout.example.test:8443/
openssl s_client -connect 127.0.0.1:8443 -servername scout.example.test -CAfile scout.crt -verify_hostname wrong.example.test </dev/null 2>&1 | grep -i verif
```

The first command prints the `scout` response. The second reports a host name mismatch.
## Common pitfalls

> [!WARNING]
> - **A certificate with a CN and no SAN.** Modern clients reject it.
> - **A Secret in the wrong namespace.** It must be in `starfleet-031-030-03-01`.
> - **Using `curl -k` to check.** It proves nothing about identity.

## Clean up

Destroy the lab cluster when you are done:

```sh
astrona destroy ats-031-lab-030-03-01
```
