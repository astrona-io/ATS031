---
exam_objectives:
- Properly set up Ingress with TLS
---
# Playground Guide: TLS Termination And Server Identity

Work in a shell on your own computer. `kubectl`, the Kubernetes command-line tool, normally already points at the playground cluster after the playground starts. A kubeconfig is the file that tells `kubectl` which cluster to use and which credentials to send. To be sure that you work on the playground and not on another cluster, select the playground's kubeconfig and check the context:

<!-- astrona:playground:renew -->

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-playground-030-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-playground-030-01" || exit 1
```

The `test` line stops the shell when the context belongs to another cluster. Keep this shell open while you work through the pages of the module.

## Look at the starting state

This playground is a `kind` cluster that runs the Traefik Ingress controller in the `ingress-system` namespace. An Ingress controller is the pod that receives HTTP and HTTPS requests from outside the cluster and forwards them to Services. The `starfleet` namespace runs the `probe` application behind the `probe` Service and holds the TLS Secret `probe-tls`. No Ingress exists yet. List the Ingresses, the Service and the last log lines of Traefik:

```sh
kubectl -n starfleet get ingress
kubectl -n starfleet get service probe
kubectl -n ingress-system logs deployment/traefik --tail=20
```

Transport Layer Security (TLS) encrypts the connection and proves the identity of the server. Traefik terminates TLS: it uses the certificate and key from the Secret, decrypts the request and forwards it over plain HTTP to the `probe` Service. A client accepts the certificate only when it trusts the certificate and the server name in the request matches a name in the certificate.

## Create the TLS Ingress

The Ingress below sends HTTPS requests for `probe.local` to the `probe` Service on port 80 and tells Traefik to use the `probe-tls` Secret on the `websecure` entry point, the HTTPS port of Traefik. Save this as `ingress-probe.yaml`:

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

Apply it:

```sh
kubectl apply -f ingress-probe.yaml
```

## Check the result

Then check the result. `kubectl describe` shows the host, the path, the backend Service and the TLS Secret that Traefik uses for the Ingress:

```sh
kubectl -n starfleet describe ingress probe
```

The `probe` Deployment and the `probe` Service stay unchanged: the Ingress only adds a route in front of them. A request from a client that trusts the certificate and sends the server name `probe.local` reaches the application. A request with another server name fails the certificate check, even though the certificate itself is trusted.


## Common pitfalls

> [!WARNING]
> Keep certificate verification enabled. Trusting a certificate still requires the correct server name. The controller terminates TLS; the application backend can remain on its ordinary HTTP listener.
