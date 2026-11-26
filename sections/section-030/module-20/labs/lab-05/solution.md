# Repair An Ingress Backend And Read The Traefik Router Name — Solution

You solve this lab with a corrected Ingress and one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Compare the port the Ingress names with the ports the Service has:

```sh
kubectl -n starfleet-031-030-02-05 get ingress beacon -o yaml
kubectl -n starfleet-031-030-02-05 get service beacon -o yaml
```

The Ingress backend names the port `web`, but the Service `beacon` has only the port `http` (number 80). Traefik cannot find a port named `web` on the Service, so it builds no router for `beacon.local`.

## Step 2: name the right Service port (check `beacon-backend`)

An Ingress backend points at a Service and one of its ports, by `name` or by `number`. The name must be a port name of the Service, not a name from the Traefik setup. Keep everything else in the Ingress as it is.

Save this as `ingress-beacon.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: beacon
  namespace: starfleet-031-030-02-05
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web
spec:
  ingressClassName: traefik
  rules:
  - host: beacon.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: beacon
            port:
              name: http
```

Apply it:

```sh
kubectl apply -f ingress-beacon.yaml
```

`port: number: 80` works as well; both name the same Service port.

## Step 3: test the route (check `beacon-route`)

Forward the Traefik HTTP port and the API port to your machine. `--resolve` sends the name `beacon.local` to the forwarded port:

```sh
kubectl -n ingress-system port-forward service/traefik 8000:80 8080:8080 >/dev/null &
curl --resolve beacon.local:8000:127.0.0.1 http://beacon.local:8000/
```

Wait a second for the port forward before `curl`. The reply must start with `app=beacon`.

## Step 4: record the router name (check `router-name`)

Traefik turns every Ingress path into a router, an internal object that matches requests with a rule such as ``Host(`beacon.local`)`` and sends them to a service. The API on port 8080 lists every HTTP router as JSON. Each router name ends with `@` and the provider that created it, here `@kubernetes`.

```sh
curl http://127.0.0.1:8080/api/http/routers
```

Find the router whose `rule` contains `beacon.local` and copy its `name` value. Use it in place of `<ROUTER>`:

```sh
kubectl -n starfleet-031-030-02-05 create configmap route-evidence --from-literal=router=<ROUTER>
```

Then check the result:

```sh
kubectl -n starfleet-031-030-02-05 get configmap route-evidence -o jsonpath='{.data.router}{"\n"}'
```

It must print the same name as the API. Stop the port forward with `kill %1`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not change the Service to add a port named `web`. Fix the Ingress: its backend must name the Service port `http` or the number 80.
>
> Keep the annotation `traefik.ingress.kubernetes.io/router.entrypoints: web`, the host `beacon.local` and the `Prefix` path `/`. The check rejects any other route.
>
> Copy the router name exactly, including `@kubernetes`. A name without the provider part does not match the API.
>
> Read the name after the route works. Before the fix, the API lists no router for `beacon.local`.
