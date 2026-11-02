---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Verify TLS Termination And Server Identity Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-01-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Inspect And Explain

The lab includes a working Traefik Ingress controller and healthy application. The required route has not been created.

Inspect the relevant evidence:

```sh
kubectl -n starfleet get ingress
kubectl -n starfleet get service probe
kubectl -n ingress-system logs deployment/traefik --tail=20
```

Transport Layer Security (TLS) authenticates the server name and protects the client connection. The Ingress controller terminates TLS with its Secret while forwarding to the application listener. A trusted certificate still requires the correct server name. The grader checks the matching response and rejects a mismatched identity.


Save this as `ingress-probe.yaml`:

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
  - host: probe.local
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
    - probe.local
    secretName: probe-tls
```

Apply the required change:

```sh
kubectl apply -f ingress-probe.yaml
```

## Verify The Result

Observe the actual result. A denied-request command returns a nonzero status when the denial works. Run denial checks separately from a shell sequence that stops on the first nonzero status.

```sh
kubectl -n starfleet get deployment probe -o yaml
```

Create a TLS Ingress `probe` for class `traefik`, host `probe.local`, Prefix path `/` and backend Service `probe` port 80. Use the supplied TLS Secret `probe-tls` and websecure entrypoint. A client trusting the supplied certificate must receive version one for the matching server name and must reject a mismatched server name. Preserve the original application and Service.

After recording the result, remove this independent lab with `astrona destroy ats-031-lab-030-01-01`.

## Common pitfalls

> [!WARNING]
> Keep certificate verification enabled. Trusting a certificate still requires the correct server name. The controller terminates TLS; the application backend can remain on its ordinary HTTP listener.
