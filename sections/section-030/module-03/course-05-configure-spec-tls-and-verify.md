---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Configure spec.tls And Verify

A Secret does nothing until an Ingress names it, and an Ingress that names it can still serve the wrong certificate. The only proof is a client that verifies the certificate. This part adds the `tls` section to an Ingress for `probe.example.test`, then tests with `curl` and `openssl s_client`, once with the correct host name and once with a wrong one.

## The tls section

The field `spec.tls` is a list. Each entry has `hosts`, a list of host names, and `secretName`, the name of the Secret in the namespace of the Ingress. The `rules` section decides where requests go, and the `tls` section decides which certificate Traefik can offer. Kubernetes does not check that the certificate contains the names listed in `hosts`. Traefik adds the certificate to its store and picks it by the name that the client asks for, so the SAN of the certificate must contain the host name.

Traefik uses two annotations for an HTTPS route. `traefik.ingress.kubernetes.io/router.entrypoints: websecure` puts the router on the HTTPS entrypoint, and `traefik.ingress.kubernetes.io/router.tls: 'true'` marks the router as a TLS router. Other controllers use other annotations, and `spec.tls` is the same everywhere.

<!-- astrona:playground:renew -->

Save this as `ingress-probe-tls.yaml`:

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

Apply it:

```sh
kubectl apply -f ingress-probe-tls.yaml
```

Then check the result. The `describe` output has a `TLS` section that names `probe-tls` and the host.

```sh
kubectl -n starfleet describe ingress probe
```

## Verify with curl

Open a second terminal, start the port forward and leave it running:

```sh
kubectl -n ingress-system port-forward service/traefik 8080:80 8443:443
```

The option `--resolve` tells `curl` to connect to `127.0.0.1:8443` while it uses the name `probe.example.test` in the URL. The client then sends that name for the TLS handshake and checks it against the certificate. The option `--cacert` makes `ca.crt` the only trusted CA. Run the command with `-v` to see the handshake:

```sh
curl -sv --cacert ca.crt --resolve probe.example.test:8443:127.0.0.1 https://probe.example.test:8443/ 2>&1 | grep -E 'subject:|issuer:|SSL certificate verify|app='
```

The output shows the subject and the issuer of the served certificate, the line that says the certificate verified, and the response from the `probe` pod. If you used a self-signed certificate, pass that certificate file to `--cacert` instead. The command `curl -k` would also succeed, but it skips the check and proves nothing.

## Verify with openssl s_client

The command `openssl s_client` opens a TLS connection and prints the certificate. The option `-servername` sends the name in the handshake, and `-verify_hostname` makes OpenSSL check the name against the SAN. Run it for the right name and for a wrong name:

```sh
openssl s_client -connect 127.0.0.1:8443 -servername probe.example.test -CAfile ca.crt -verify_hostname probe.example.test </dev/null 2>&1 | grep -i 'verif'
openssl s_client -connect 127.0.0.1:8443 -servername probe.example.test -CAfile ca.crt -verify_hostname wrong.example.test </dev/null 2>&1 | grep -i 'verif'
```

The first command ends with `Verify return code: 0 (ok)`. The second reports a host name mismatch. The chain and the dates are the same in both, so the name alone causes the failure. To print the served certificate itself, pipe the output into `openssl x509 -noout -subject -issuer -ext subjectAltName`.

You have a working HTTPS route and have seen verification pass and fail. The next question is what a client receives when the Secret or the name is wrong, and how to send HTTP clients to HTTPS.

## Common pitfalls

> [!WARNING]
> - **Using `curl -k` to make a test pass.** It skips the identity check.
> - **A SAN that does not contain the host.** The route works but the client rejects the certificate.
> - **Missing `router.tls` or a wrong entrypoint.** The router is not a TLS router, or listens on the HTTP entrypoint.
> - **Port forward not running.** A refused connection on `127.0.0.1:8443` means the forward stopped.
