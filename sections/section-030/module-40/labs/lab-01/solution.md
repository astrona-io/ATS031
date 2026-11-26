# Require TLS 1.3 And Strict Server Names — Solution

You solve this lab with one change to the Traefik TLS options and a restart of Traefik. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Read the current TLS options and the way Traefik loads them:

```sh
kubectl -n ingress-system get configmap traefik-dynamic -o yaml
kubectl -n ingress-system get deployment traefik -o jsonpath='{.spec.template.spec.containers[0].args}'; echo
kubectl -n starfleet-031-030-04-01 get ingress probe
```

The file `dynamic.yaml` sets only `minVersion: VersionTLS12` for the TLS option `default`. Traefik reads it with the file provider from `/etc/traefik/dynamic`, where the ConfigMap is mounted.

## Step 2: set TLS 1.3 and strict server names (check `tls-option`)

A TLS option in Traefik is a named set of rules for the TLS handshake. The option `default` applies to every route that names no other option, so the Ingress `probe` needs no change. `minVersion: VersionTLS13` makes Traefik refuse every client that offers only TLS 1.2 or older. `sniStrict: true` makes Traefik refuse a handshake when the client asks for a server name (Server Name Indication, SNI) that matches no certificate, instead of sending its own default certificate.

Save this as `dynamic.yaml`:

```yaml
tls:
  options:
    default:
      minVersion: VersionTLS13
      sniStrict: true
```

Write it into the ConfigMap. The command builds the ConfigMap from the file and applies it over the old one:

```sh
kubectl -n ingress-system create configmap traefik-dynamic --from-file=dynamic.yaml --dry-run=client -o yaml | kubectl apply -f -
```

Then restart Traefik, so it reads the new file at once:

```sh
kubectl -n ingress-system rollout restart deployment/traefik
kubectl -n ingress-system rollout status deployment/traefik --timeout=180s
```

## Step 3: test the TLS versions (check `tls13-minimum`)

Start a port forward to the Traefik HTTPS port in another terminal:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443
```

Save the certificate from the Secret, so `curl` can trust it, then send one request over TLS 1.3 and one that allows at most TLS 1.2:

```sh
kubectl -n starfleet-031-030-04-01 get secret probe-tls -o jsonpath='{.data.tls\.crt}' | base64 -d > probe.crt
curl --cacert probe.crt --resolve probe.example.test:8443:127.0.0.1 https://probe.example.test:8443/
curl --cacert probe.crt --tls-max 1.2 --resolve probe.example.test:8443:127.0.0.1 https://probe.example.test:8443/
```

The first command must print a line that starts with `app=probe`. The second must fail with a TLS handshake error and print no reply.

## Step 4: test an unknown server name (check `sni-strict`)

Ask for a name that no Ingress serves. `-k` skips the certificate check here on purpose: the test must show that Traefik refuses the handshake itself, not that `curl` rejects a certificate.

```sh
curl -k --resolve unknown.example.test:8443:127.0.0.1 https://unknown.example.test:8443/
```

The command must fail with a TLS handshake error and print no reply. Stop the port forward with Ctrl+C.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Put both settings under the option `default`. An option with another name applies only to routes that name it, so the Ingress `probe` keeps TLS 1.2 and the default certificate.
>
> Changing the ConfigMap is not enough on its own. If Traefik has not loaded the new file, a TLS 1.2 handshake and a handshake for `unknown.example.test` still succeed. Restart the Deployment `traefik`.
>
> Use the exact value `VersionTLS13`, the name Traefik expects, not another spelling such as `TLS1.3`.
>
> Do not edit the Ingress `probe` or the Secret `probe-tls`: `https://probe.example.test` must keep answering over TLS 1.3 with the `probe-tls` certificate.
