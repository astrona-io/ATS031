# Several Services And A Default Backend

A real cluster publishes many Services on one address. An Ingress can send each path or each host to a different Service. It can also name one Service that answers every request that no other rule matches.

On this page, you build both. You also see how the two ways to split traffic differ, and what a client gets for an unknown host or path.

## Fan-out by path and by host

The Ingress API has two ways to split traffic between Services, and you write both in `spec.rules`:

- A **fan-out** is one host with several paths, and each path goes to its own Service. For a fan-out, one rule has several `paths`.
- A **name-based virtual host** setup is several hosts, each with its own rules. For this setup, `rules` has several entries with different `host` values.

A rule without a `host` matches every host. It is the usual way to catch requests for names you did not list.

The field `spec.defaultBackend` names a Service that receives every request that no rule matches. Traefik supports it as a catch-all router with the lowest priority. Only one Ingress of a class should define a default backend. Two definitions compete, and you cannot predict which one wins.

<!-- astrona:playground:renew -->

Save this as `ingress-bridge.yaml`. It publishes `probe` under `/probe` and `scout` under `/scout` on the host `bridge.local`, and it sends everything else to `scout`.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bridge
  namespace: starfleet
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web
spec:
  ingressClassName: traefik
  defaultBackend:
    service:
      name: scout
      port:
        number: 80
  rules:
  - host: bridge.local
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
kubectl apply -f ingress-bridge.yaml
```

Start the port forward in a second terminal if it is not running:

```sh
kubectl -n ingress-system port-forward service/traefik 8080:80 8443:443
```

Then send four requests: both paths on the listed host, an unknown path on the listed host, and an unknown host.

```sh
curl -s -H 'Host: bridge.local' http://127.0.0.1:8080/probe
curl -s -H 'Host: bridge.local' http://127.0.0.1:8080/scout
curl -s -H 'Host: bridge.local' http://127.0.0.1:8080/unknown
curl -s -H 'Host: elsewhere.local' http://127.0.0.1:8080/
```

The first request returns `app=probe`, and the second returns `app=scout`. The third and the fourth also return `app=scout`. The default backend answers every request that matches no rule, and that includes requests for a host that no rule names. Without the `defaultBackend` field, the third and the fourth requests would return the Traefik `404 page not found`.

![Diagram: requests to bridge.local /probe go to the probe Service, bridge.local /scout goes to the scout Service, and every request that matches no rule, such as bridge.local /unknown or elsewhere.local, goes to the default backend scout](images/default-backend-fanout.svg)

The drawing shows that the two rules take their requests first. The default backend takes all the rest.

## When a backend is missing

A route can also fail on the backend side, after a rule has matched. If a rule names a Service that does not exist, the API server still accepts the Ingress. Traefik cannot build the backend, so it returns an error status for that route and logs the reason.

If the Service exists but has no ready pod, the route exists, and the request fails with `503`. So read the Service and its EndpointSlices before you blame the Ingress.

You can now publish several Services from one host and decide what unmatched requests receive. The graded task on the next page asks you to build a similar set of routes yourself. The open question is how to see what Traefik itself did with each request.

## Common pitfalls

> [!WARNING]
> - **Two default backends in one class.** Only one Ingress of a class should define `defaultBackend`.
> - **A host rule hidden by a rule without a host.** Check which rule is more specific when two rules overlap.
> - **Naming a Service in another namespace.** An Ingress backend must be in the namespace of the Ingress.
> - **Mixing up a 404 from Traefik and a 404 from the pod.** The body text tells them apart: Traefik answers `404 page not found`.
