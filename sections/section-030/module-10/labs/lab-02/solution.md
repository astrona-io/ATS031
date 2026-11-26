# Fix An Ingress That Traefik Ignores — Solution

You solve this lab by fixing two fields of one Ingress. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Read the class and the backend port of the Ingress, then compare them with the classes in the cluster and the ports of the Service:

```sh
kubectl -n starfleet-031-030-01-02 get ingress relay -o jsonpath='{.spec.ingressClassName} {.spec.rules[0].http.paths[0].backend.service.port.number}{"\n"}'
kubectl get ingressclass
kubectl -n starfleet-031-030-01-02 get service relay -o jsonpath='{.spec.ports[0].port}{"\n"}'
```

The first command prints `nginx 8080`. The cluster has only the IngressClass `traefik`, and the Service `relay` listens on port `80`.

## Step 2: name the traefik class (check `relay-class`)

An IngressClass names the controller that serves an Ingress. Traefik in this lab watches only Ingresses with `spec.ingressClassName: traefik`. The Ingress names `nginx`, and no controller serves that class, so Traefik ignores the object and answers `404` for every host. Change the class to `traefik`.

## Step 3: point the backend at the Service port (check `relay-backend`)

An Ingress backend names a Service and a port of that Service, not a port of the container. The Service `relay` listens on port 80 and forwards to container port 8080, so the backend must say 80. Keep the host, the path and the `web` entrypoint annotation as they are.

Save this as `ingress-relay.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: relay
  namespace: starfleet-031-030-01-02
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web
spec:
  ingressClassName: traefik
  rules:
  - host: relay.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: relay
            port:
              number: 80
```

Apply it:

```sh
kubectl apply -f ingress-relay.yaml
```

## Step 4: test the right and the wrong host (check `relay-routing`)

Forward the Traefik HTTP port to your machine:

```sh
kubectl -n ingress-system port-forward service/traefik 8080:80 >/dev/null &
```

Wait a second for the port forward, then send one request with the right host and one with another host:

```sh
curl -s -H 'Host: relay.local' http://127.0.0.1:8080/
curl -s -o /dev/null -w '%{http_code}\n' -H 'Host: other.local' http://127.0.0.1:8080/
```

The first request prints a line that starts with `app=relay`. The second prints `404`. Stop the port forward with `kill %1`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Fix both mistakes. With the wrong class, Traefik ignores the Ingress. With the container port 8080 as the backend port, the route does not reach the Service `relay`.
>
> Do not remove the annotation `traefik.ingress.kubernetes.io/router.entrypoints: web` or change the host or the path. The check expects them unchanged.
>
> Test with a `Host` header. Traefik matches the host name, so a request to `127.0.0.1` without the header gets `404`.
