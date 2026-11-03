---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Path Types And Priority

One host often serves several paths, and a request can match more than one rule. The result then depends on the path type and on which rule the controller prefers. A wrong choice sends requests to the wrong Service or hides a Service completely. This part explains the path types of the Ingress API, shows how Traefik chooses between overlapping rules, and tests the boundary cases with real requests.

## The three path types

The `pathType` field is required for every path. `Exact` matches only the identical path, so `/exact` does not match `/exact/` or `/exact/more`. `Prefix` matches by path elements, which are the parts separated by `/`. The prefix `/api` matches `/api` and `/api/v1`, and the Kubernetes specification says it must not match `/apiary`. `ImplementationSpecific` leaves the decision to the controller, so a task that needs predictable behavior uses `Prefix` or `Exact`.

When several paths of one Ingress match a request, the specification says the longest matching path wins, and `Exact` wins over `Prefix` for the same path. Traefik implements this by giving each router a priority. By default the priority is the length of the generated rule, so a rule with a longer path has a higher priority. The annotation `traefik.ingress.kubernetes.io/router.priority` sets the priority by hand when the default is not enough.

## Test overlapping paths

The Ingress below has three paths on the host `paths.local`. The path `/` goes to `probe`, the path `/api` goes to `scout`, and the exact path `/exact` goes to `scout`.

<!-- astrona:playground:renew -->

Save this as `ingress-paths.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: paths
  namespace: starfleet
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web
spec:
  ingressClassName: traefik
  rules:
  - host: paths.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: probe
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: scout
            port:
              number: 80
      - path: /exact
        pathType: Exact
        backend:
          service:
            name: scout
            port:
              number: 80
```

Apply it:

```sh
kubectl apply -f ingress-paths.yaml
```

Start the port forward in a second terminal if it is not running. Then send requests in the first terminal. Each response starts with the `app` name of the Service that answered.

```sh
kubectl -n ingress-system port-forward service/traefik 8080:80 8443:443
```

```sh
for path in / /other /api /api/v1 /apiary /exact /exact/ /exact/more; do
  printf '%s -> ' "$path"
  curl -s -H 'Host: paths.local' "http://127.0.0.1:8080$path" | cut -d' ' -f1
done
```

The paths `/` and `/other` return `app=probe`, because only the prefix `/` matches them. The paths `/api` and `/api/v1` return `app=scout`, because `/api` is longer than `/`. The path `/exact` returns `app=scout`, but `/exact/` and `/exact/more` return `app=probe`, because the exact rule does not match them and the prefix `/` does.

The path `/apiary` is the boundary case. The specification says it must not match the prefix `/api`, so the correct answer is `app=probe`. If your version of Traefik returns `app=scout`, it treats the prefix as a plain text prefix. Compare the result with the specification and do not assume the controller follows it.

## What the backend receives

Each response ends with the `path` field that the pod received. The pod sees the path exactly as the client sent it, including `/api`. Traefik does not remove the prefix by default. Removing or rewriting a path is the job of a middleware, such as the strip-prefix middleware. A middleware is a separate Traefik object, and an Ingress refers to it with the annotation `traefik.ingress.kubernetes.io/router.middlewares`. If a backend expects the path without the prefix, a missing middleware shows up as a `404` that comes from the application, not from Traefik.

You can now predict which rule handles a request. The next question is how to publish several Services from one host and what to do with requests that match no rule.

## Common pitfalls

> [!WARNING]
> - **Leaving out `pathType`.** The API server rejects an Ingress path without it.
> - **Trusting `Prefix` without testing the boundary.** Check `/apiary` against `/api` in the controller you use.
> - **Expecting the prefix to be removed.** The backend gets the full path unless a middleware changes it.
> - **Relying on `ImplementationSpecific`.** Its meaning differs between controllers.
