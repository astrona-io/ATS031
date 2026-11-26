# Publish One Host Over HTTP Only — Solution

You solve this lab with one Ingress. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the Service, the Ingress class and the Traefik entrypoints, and that no Ingress exists yet:

```sh
kubectl -n starfleet-031-030-02-03 get deployment,service depot
kubectl get ingressclass traefik
kubectl -n ingress-system get deployment traefik -o jsonpath='{.spec.template.spec.containers[0].args}{"\n"}'
kubectl -n starfleet-031-030-02-03 get ingress
```

Traefik has two entrypoints, the ports it listens on: `web` on container port 8000 for HTTP and `websecure` on container port 8443 for HTTPS. The Service `traefik` publishes them on ports 80 and 443.

## Step 2: create the Ingress on the web entrypoint (check `depot-ingress`)

An Ingress is a Kubernetes object that tells an Ingress controller how to route HTTP requests to Services. Without an entrypoint annotation, Traefik attaches the route to every entrypoint, so it would also answer over HTTPS. The annotation `traefik.ingress.kubernetes.io/router.entrypoints: web` limits the route to HTTP. The `Prefix` path `/` matches every path of `depot.local`.

Save this as `ingress-depot.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: depot
  namespace: starfleet-031-030-02-03
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web
spec:
  ingressClassName: traefik
  rules:
  - host: depot.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: depot
            port:
              number: 80
```

Apply it:

```sh
kubectl apply -f ingress-depot.yaml
```

## Step 3: test HTTP for depot.local (check `depot-http`)

Forward both Traefik ports to your machine. `--resolve` sends the host names to the forwarded ports:

```sh
kubectl -n ingress-system port-forward service/traefik 8000:80 8443:443 >/dev/null &
curl --resolve depot.local:8000:127.0.0.1 http://depot.local:8000/manifest
```

Wait a second for the port forward before `curl`. The reply must start with `app=depot`.

## Step 4: test other hosts and HTTPS (check `depot-404`)

A request that matches no router gets 404 from Traefik itself. Send one HTTP request for another host and one HTTPS request for `depot.local`. The HTTPS request uses `-k` because no certificate exists for `depot.local`: Traefik answers the handshake with its own default certificate, and this test only looks at the status code:

```sh
curl -s -o /dev/null -w '%{http_code}\n' --resolve other.local:8000:127.0.0.1 http://other.local:8000/
curl -k -s -o /dev/null -w '%{http_code}\n' --resolve depot.local:8443:127.0.0.1 https://depot.local:8443/
```

Both commands must print `404`. Stop the port forward with `kill %1`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Without the annotation `traefik.ingress.kubernetes.io/router.entrypoints: web`, the route also answers on `websecure`, so the HTTPS request no longer gets 404. The value must be exactly `web`, not `web,websecure`.
>
> Do not leave out `host: depot.local`. A rule without a host matches every host, so the request for another host no longer gets 404.
>
> The Ingress must have exactly one rule and one path. Use the Service port 80, not the container port 8080.
