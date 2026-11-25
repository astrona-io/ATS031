---
exam_objectives:
- Properly set up Ingress with TLS
---
# Serve Two Hosts With Their Own Certificates Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-01-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-01-04" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Find the mistake

Read the `tls` section and the SAN of each certificate:

```sh
kubectl -n starfleet-031-030-01-04 get ingress fleet -o jsonpath='{range .spec.tls[*]}{.hosts} {.secretName}{"\n"}{end}'
kubectl -n starfleet-031-030-01-04 get secret dock-tls -o jsonpath='{.data.tls\.crt}' | base64 --decode > dock.crt
openssl x509 -in dock.crt -noout -ext subjectAltName
```

The single entry lists both hosts with `bridge-tls`, so the certificate for `dock.local` is never loaded. Traefik picks a certificate by the server name in the TLS handshake, which is called Server Name Indication (SNI). No loaded certificate names `dock.local`, so Traefik sends its default certificate.

## Give each host its own entry

Save this as `ingress-fleet.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fleet
  namespace: starfleet-031-030-01-04
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    traefik.ingress.kubernetes.io/router.tls: 'true'
spec:
  ingressClassName: traefik
  rules:
  - host: bridge.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: bridge
            port:
              number: 80
  - host: dock.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: dock
            port:
              number: 80
  tls:
  - hosts:
    - bridge.local
    secretName: bridge-tls
  - hosts:
    - dock.local
    secretName: dock-tls
```

Apply it:

```sh
kubectl apply -f ingress-fleet.yaml
```

Then check the result. Open a port forward in a second terminal and ask for each server name. The `subject` line names the host that you asked for:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443
openssl s_client -connect 127.0.0.1:8443 -servername dock.local </dev/null 2>/dev/null | grep '^subject'
curl -s --cacert dock.crt --resolve dock.local:8443:127.0.0.1 https://dock.local:8443/
```

The `curl` response starts with `app=dock`.

## Common pitfalls

> [!WARNING]
> - **Listing several hosts with one Secret.** The certificate in that Secret must name every host in its SAN, otherwise clients reject it.
> - **Testing without `-servername`.** Without SNI, Traefik cannot pick the host certificate and sends its default certificate.
> - **Editing the rules instead of `tls`.** The routes were correct; only the certificate selection was wrong.

## Clean up

Destroy the lab cluster when you are done:

```sh
astrona destroy ats-031-lab-030-01-04
```
