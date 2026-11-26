# Require Client Certificates On One Route — Solution

You solve this lab with a new ConfigMap, a new TLS option, one annotation and a restart of Traefik. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Read the TLS options, the Traefik volumes and the two Ingresses:

```sh
kubectl -n ingress-system get configmap traefik-dynamic -o yaml
kubectl -n ingress-system get deployment traefik -o jsonpath='{.spec.template.spec.volumes}'; echo
kubectl -n starfleet-031-030-04-03 get ingress vault beacon
kubectl -n starfleet-031-030-04-03 get secret crew-client
```

Traefik mounts the ConfigMap `client-ca` at `/etc/traefik/client-ca`, but the ConfigMap does not exist yet; the volume is marked `optional: true`, so Traefik starts without it. `dynamic.yaml` has only the option `default`.

## Step 2: give Traefik the CA and the mtls option (check `mtls-option`)

Mutual TLS (mTLS) means that the client also shows a certificate in the TLS handshake. Traefik checks that certificate against a CA file. Copy the crew CA from the Secret into the ConfigMap `client-ca`:

```sh
kubectl -n starfleet-031-030-04-03 get secret crew-client -o jsonpath='{.data.ca\.crt}' | base64 -d > client-ca.crt
kubectl -n ingress-system create configmap client-ca --from-file=client-ca.crt=client-ca.crt
```

Now add the TLS option `mtls`. `clientAuthType: RequireAndVerifyClientCert` makes Traefik refuse a client that sends no certificate or a certificate that the CA files did not sign. The option `default` stays as it was, so other routes do not ask for a client certificate.

Save this as `dynamic.yaml`:

```yaml
tls:
  options:
    default:
      minVersion: VersionTLS12
    mtls:
      minVersion: VersionTLS12
      clientAuth:
        clientAuthType: RequireAndVerifyClientCert
        caFiles:
        - /etc/traefik/client-ca/client-ca.crt
```

Write it into the ConfigMap `traefik-dynamic`:

```sh
kubectl -n ingress-system create configmap traefik-dynamic --from-file=dynamic.yaml --dry-run=client -o yaml | kubectl apply -f -
```

## Step 3: attach the option to vault (check `vault-annotation`)

A route uses the option `default` unless it names another one. The annotation `traefik.ingress.kubernetes.io/router.tls.options: mtls@file` names the option `mtls` from the file provider (`@file`). Only `vault` gets it.

Save this as `ingress-vault.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vault
  namespace: starfleet-031-030-04-03
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    traefik.ingress.kubernetes.io/router.tls: 'true'
    traefik.ingress.kubernetes.io/router.tls.options: mtls@file
spec:
  ingressClassName: traefik
  rules:
  - host: vault.example.test
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: vault
            port:
              number: 80
  tls:
  - hosts:
    - vault.example.test
    secretName: vault-tls
```

Apply it:

```sh
kubectl apply -f ingress-vault.yaml
```

Then restart Traefik, so it mounts the new ConfigMap `client-ca` and reads the new `dynamic.yaml`:

```sh
kubectl -n ingress-system rollout restart deployment/traefik
kubectl -n ingress-system rollout status deployment/traefik --timeout=180s
```

## Step 4: test with and without a client certificate (check `mtls-enforced`)

Start a port forward to the Traefik HTTPS port in another terminal:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443
```

Save the server certificates and the client certificate and key from the Secrets:

```sh
kubectl -n starfleet-031-030-04-03 get secret vault-tls -o jsonpath='{.data.tls\.crt}' | base64 -d > vault.crt
kubectl -n starfleet-031-030-04-03 get secret beacon-tls -o jsonpath='{.data.tls\.crt}' | base64 -d > beacon.crt
kubectl -n starfleet-031-030-04-03 get secret crew-client -o jsonpath='{.data.tls\.crt}' | base64 -d > crew.crt
kubectl -n starfleet-031-030-04-03 get secret crew-client -o jsonpath='{.data.tls\.key}' | base64 -d > crew.key
```

Send three requests:

```sh
curl -s --cacert vault.crt --resolve vault.example.test:8443:127.0.0.1 https://vault.example.test:8443/ ; echo "exit=$?"
curl -s --cacert vault.crt --cert crew.crt --key crew.key --resolve vault.example.test:8443:127.0.0.1 https://vault.example.test:8443/
curl -s --cacert beacon.crt --resolve beacon.example.test:8443:127.0.0.1 https://beacon.example.test:8443/
```

The first request has no client certificate. It must fail with no reply and a nonzero exit status; the exact error depends on the TLS version, so read the status. The second must print a line that starts with `app=vault`, and the third a line that starts with `app=beacon`. Stop the port forward with Ctrl+C.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not add `clientAuth` to the option `default`. Every route without its own option uses `default`, so `beacon` would then refuse clients without a certificate too.
>
> The annotation must say `mtls@file`, not `mtls`. The option lives in the file provider, and the Ingress must name the provider.
>
> The ConfigMap `client-ca` must hold the CA certificate (`ca.crt` of `crew-client`), not the client certificate, under the key `client-ca.crt`. The path in `caFiles` must be `/etc/traefik/client-ca/client-ca.crt`.
>
> Restart the Deployment `traefik` after you create the ConfigMap `client-ca`. The restart makes the new pod mount the CA file and load `dynamic.yaml` at once; until Traefik has the CA file, `vault` cannot verify the crew certificate.
