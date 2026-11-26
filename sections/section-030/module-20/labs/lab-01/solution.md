# Route Two Paths Of One Host With An Ingress — Solution

You solve this lab with one Ingress. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the two Services, the Ingress class, and that no Ingress exists yet:

```sh
kubectl -n starfleet-031-030-02-01 get deployment,service
kubectl get ingressclass traefik
kubectl -n starfleet-031-030-02-01 get ingress
```

The Services `probe` and `scout` listen on port 80 and send traffic to their pods on port 8080. Each pod replies with a line that starts with `app=probe` or `app=scout`, so you can see which Service answered.

## Step 2: create the Ingress with two paths (check `fleet-ingress`)

An Ingress is a Kubernetes object that tells an Ingress controller how to route HTTP requests to Services. `spec.ingressClassName: traefik` hands this Ingress to the Traefik controller. One rule for the host `fleet.local` holds two paths. The path type `Prefix` matches the path and everything below it, so `/probe` also matches `/probe/status`.

Save this as `ingress-fleet.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fleet
  namespace: starfleet-031-030-02-01
spec:
  ingressClassName: traefik
  rules:
  - host: fleet.local
    http:
      paths:
      - path: /probe
        pathType: Prefix
        backend:
          service:
            name: probe
            port:
              number: 80
      - path: /scout
        pathType: Prefix
        backend:
          service:
            name: scout
            port:
              number: 80
```

Apply it:

```sh
kubectl apply -f ingress-fleet.yaml
```

## Step 3: check that each path reaches its Service (check `path-routing`)

Traefik reads the Ingress and builds one router per path. It picks the router from the `Host` header and the path of each request. Forward the Traefik HTTP port to your machine, then send one request to each path. `--resolve` sends the name `fleet.local` to the forwarded port:

```sh
kubectl -n ingress-system port-forward service/traefik 8000:80 >/dev/null &
curl --resolve fleet.local:8000:127.0.0.1 http://fleet.local:8000/probe
curl --resolve fleet.local:8000:127.0.0.1 http://fleet.local:8000/scout
```

Wait a second for the port forward before the first `curl`. The first reply must start with `app=probe`, the second with `app=scout`.

## Step 4: check that nothing else matches (check `unmatched-404`)

A request that matches no router gets 404 from Traefik itself; it never reaches a pod. Send one request for another host and one for another path:

```sh
curl -s -o /dev/null -w '%{http_code}\n' --resolve other.local:8000:127.0.0.1 http://other.local:8000/probe
curl -s -o /dev/null -w '%{http_code}\n' --resolve fleet.local:8000:127.0.0.1 http://fleet.local:8000/other
```

Both commands must print `404`. Stop the port forward with `kill %1`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not leave out `host: fleet.local`. A rule without a host matches every host, so the request for `other.local` no longer gets 404.
>
> Do not add a catch-all path such as `/`. Then `fleet.local/other` reaches a Service instead of getting 404.
>
> Use the Service port 80 in the backend, not the container port 8080, and keep `pathType: Prefix` on both paths.
>
> Do not edit the Deployments or Services `probe` and `scout`. The checks expect them unchanged.
