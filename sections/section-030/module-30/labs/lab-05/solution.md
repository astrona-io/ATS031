# Redirect HTTP To HTTPS And Add An HSTS Header — Solution

You solve this lab with a new `dynamic.yaml`, one Ingress update and one patch of the Traefik Deployment. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the dynamic configuration, the Traefik arguments and the Ingress annotations:

```sh
kubectl -n ingress-system get configmap traefik-dynamic -o jsonpath='{.data.dynamic\.yaml}'
kubectl -n ingress-system get deployment traefik -o jsonpath='{.spec.template.spec.containers[0].args}{"\n"}'
kubectl -n starfleet-031-030-03-05 get ingress harbor -o jsonpath='{.metadata.annotations}{"\n"}'
```

Traefik mounts the ConfigMap `traefik-dynamic` at `/etc/traefik/dynamic` and reads it with its file provider (`--providers.file.directory` and `--providers.file.watch=true`). Today the file holds only the TLS option `default`.

## Step 2: define the hsts middleware (check `hsts-middleware`)

A middleware is a Traefik step that changes a request or a response on a route. The `headers` middleware with `stsSeconds: 300` adds the response header `Strict-Transport-Security: max-age=300`. HTTP Strict Transport Security (HSTS) tells the browser to use only HTTPS for this host for the next 300 seconds. Keep the TLS option `default` in the same file.

Save this as `dynamic.yaml`:

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

Replace the ConfigMap with the new file. The key name comes from the file name, so the file must be called `dynamic.yaml`:

```sh
kubectl -n ingress-system create configmap traefik-dynamic --from-file=dynamic.yaml --dry-run=client -o yaml | kubectl apply -f -
```

## Step 3: attach the middleware to the Ingress (check `hsts-header`)

A middleware from the file provider has the name `<name>@file`. The annotation `traefik.ingress.kubernetes.io/router.middlewares: hsts@file` adds it to the route Traefik builds for the Ingress `harbor`. The rest of the Ingress stays as it was.

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

## Step 4: redirect the web entrypoint to HTTPS (check `https-redirect`)

An entrypoint is a port Traefik listens on: `web` on 8000 for HTTP and `websecure` on 8443 for HTTPS. Two arguments make Traefik answer every request on `web` with a permanent redirect to `websecure` with the scheme `https`. A JSON patch with the operation `add` and the path `args/-` appends them and keeps every existing argument.

Save this as `traefik-redirect-patch.json`:

```json
[
  {"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--entryPoints.web.http.redirections.entryPoint.to=websecure"},
  {"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--entryPoints.web.http.redirections.entryPoint.scheme=https"}
]
```

Apply it and wait for the new Traefik pod:

```sh
kubectl -n ingress-system patch deployment traefik --type=json --patch-file traefik-redirect-patch.json
kubectl -n ingress-system rollout status deployment/traefik --timeout=180s
```

## Step 5: test the header and the redirect (checks `hsts-header` and `https-redirect`)

Save the certificate from the Secret, so `curl` can trust it, and forward both Traefik ports to your machine:

```sh
kubectl -n starfleet-031-030-03-05 get secret harbor-tls -o jsonpath='{.data.tls\.crt}' | base64 -d > harbor.crt
kubectl -n ingress-system port-forward service/traefik 8080:80 8443:443 >/dev/null &
```

Wait a second for the port forward, then send one HTTPS and one HTTP request. `-i` prints the response headers:

```sh
curl -si --cacert harbor.crt --resolve harbor.example.test:8443:127.0.0.1 https://harbor.example.test:8443/
curl -si --resolve harbor.example.test:8080:127.0.0.1 http://harbor.example.test:8080/cargo
```

The HTTPS response must have the status `200`, the header `Strict-Transport-Security: max-age=300` and a body that starts with `app=harbor`. The HTTP response must have the status `301` or `308` and a `Location` header that starts with `https://harbor.example.test` and ends with `/cargo`. Stop the port forward with `kill %1`.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not drop the TLS option `default` when you write the new `dynamic.yaml`. The check requires it with `minVersion: VersionTLS12`.
>
> The annotation value must be exactly `hsts@file`. Without the `@file` suffix, Traefik looks for the middleware in the wrong provider.
>
> A strategic merge patch or `kubectl edit` that replaces the `args` list can lose an existing argument. The check requires all of them, such as `--providers.file.directory=/etc/traefik/dynamic` and `--entrypoints.websecure.address=:8443`.
>
> A redirect with the status `302` is temporary and fails. The entrypoint redirection is permanent by default.
