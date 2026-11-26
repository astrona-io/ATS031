# Route An Exact Path And A Prefix Path — Solution

You solve this lab with one Ingress. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the two Services and the Ingress class, and that no Ingress exists yet:

```sh
kubectl -n starfleet-031-030-02-04 get deployment,service
kubectl get ingressclass traefik
kubectl -n starfleet-031-030-02-04 get ingress
```

The Services `beacon` and `scout` listen on port 80. Each pod replies with a line that starts with `app=beacon` or `app=scout`, so you can see which Service answered.

## Step 2: create the Ingress with two path types (check `api-ingress`)

An Ingress is a Kubernetes object that tells an Ingress controller how to route HTTP requests to Services. Each path has a `pathType`. `Exact` matches only that one path, letter for letter. `Prefix` matches the path and every path below it, split at `/`: `/v1` matches `/v1` and `/v1/ships/7`, but not `/v2`. The annotation `traefik.ingress.kubernetes.io/router.entrypoints: web` puts the routes on the HTTP entrypoint of Traefik.

Save this as `ingress-api.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api
  namespace: starfleet-031-030-02-04
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web
spec:
  ingressClassName: traefik
  rules:
  - host: api.local
    http:
      paths:
      - path: /healthz
        pathType: Exact
        backend:
          service:
            name: beacon
            port:
              number: 80
      - path: /v1
        pathType: Prefix
        backend:
          service:
            name: scout
            port:
              number: 80
```

Apply it:

```sh
kubectl apply -f ingress-api.yaml
```

## Step 3: test the Exact path (check `exact-path`)

Forward the Traefik HTTP port to your machine. `--resolve` sends the name `api.local` to the forwarded port:

```sh
kubectl -n ingress-system port-forward service/traefik 8000:80 >/dev/null &
curl --resolve api.local:8000:127.0.0.1 http://api.local:8000/healthz
curl -s -o /dev/null -w '%{http_code}\n' --resolve api.local:8000:127.0.0.1 http://api.local:8000/healthz/deep
```

Wait a second for the port forward before the first `curl`. The first reply must start with `app=beacon`. The second command must print `404`, because `Exact` does not match a longer path.

## Step 4: test the Prefix path (check `prefix-path`)

```sh
curl --resolve api.local:8000:127.0.0.1 http://api.local:8000/v1
curl --resolve api.local:8000:127.0.0.1 http://api.local:8000/v1/ships/7
curl -s -o /dev/null -w '%{http_code}\n' --resolve api.local:8000:127.0.0.1 http://api.local:8000/v2
curl -s -o /dev/null -w '%{http_code}\n' --resolve api.local:8000:127.0.0.1 http://api.local:8000/
```

The first two replies must start with `app=scout`. The last two commands must print `404`: no path matches them, so Traefik answers itself. Stop the port forward with `kill %1`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not use `Prefix` for `/healthz`. Then `/healthz/deep` reaches `beacon` instead of getting 404.
>
> Do not add a path `/` or any other path. The check wants exactly the two paths, and `/` must get 404.
>
> Do not leave out the annotation `traefik.ingress.kubernetes.io/router.entrypoints: web` or the class `traefik`. The check reads both.
>
> Use the Service port 80 in both backends, not the container port 8080.
