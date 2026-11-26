# Repair The Ingress Controller Class And Its RBAC — Solution

You solve this lab with one JSON patch to the Deployment `traefik` and one ClusterRole. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Read the controller arguments, the ClusterRole and the Ingress:

```sh
kubectl -n ingress-system get deployment traefik -o jsonpath='{.spec.template.spec.containers[0].args}{"\n"}'
kubectl get clusterrole traefik -o yaml
kubectl get ingressclass traefik
kubectl -n starfleet-031-030-02-02 get ingress cargo -o yaml
```

The second argument is `--providers.kubernetesingress.ingressclass=traefik-internal`, but the Ingress `cargo` uses the class `traefik`. The ClusterRole has no rule for `endpointslices`.

## Step 2: watch the right IngressClass (check `controller-class`)

The argument `--providers.kubernetesingress.ingressclass` tells Traefik which IngressClass it serves. Traefik ignores every Ingress of another class, so with `traefik-internal` it never builds a router for `cargo`. A JSON patch changes only that one list item. The `test` operation first makes sure the item at index 1 has the old value, so the patch cannot replace the wrong argument.

Save this as `traefik-class-patch.json`:

```json
[
  {"op": "test", "path": "/spec/template/spec/containers/0/args/1", "value": "--providers.kubernetesingress.ingressclass=traefik-internal"},
  {"op": "replace", "path": "/spec/template/spec/containers/0/args/1", "value": "--providers.kubernetesingress.ingressclass=traefik"}
]
```

Apply it and wait for the new Traefik pod:

```sh
kubectl -n ingress-system patch deployment traefik --type=json --patch-file traefik-class-patch.json
kubectl -n ingress-system rollout status deployment/traefik --timeout=180s
```

## Step 3: let Traefik read EndpointSlices (check `controller-rbac`)

An EndpointSlice is a Kubernetes object that lists the pod addresses behind a Service. Traefik reads EndpointSlices to send requests straight to the pods. Without read access, it finds no address for the Service `cargo`. Role-based access control (RBAC) grants this access through the ClusterRole `traefik`, which the ClusterRoleBinding `traefik` gives to the ServiceAccount `traefik`. Add one rule for `endpointslices` in the API group `discovery.k8s.io` with only the read verbs.

Save this as `clusterrole-traefik.yaml`:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: traefik
rules:
- apiGroups:
  - ''
  resources:
  - services
  - endpoints
  - secrets
  - namespaces
  - nodes
  verbs:
  - get
  - list
  - watch
- apiGroups:
  - discovery.k8s.io
  resources:
  - endpointslices
  verbs:
  - get
  - list
  - watch
- apiGroups:
  - networking.k8s.io
  resources:
  - ingresses
  - ingressclasses
  verbs:
  - get
  - list
  - watch
```

Apply it:

```sh
kubectl apply -f clusterrole-traefik.yaml
```

Then check the access as the ServiceAccount:

```sh
kubectl auth can-i list endpointslices.discovery.k8s.io --all-namespaces --as=system:serviceaccount:ingress-system:traefik
```

It must print `yes`.

## Step 4: test the route (check `cargo-routing`)

Forward the Traefik HTTP port to your machine and send a request for `cargo.local`. `--resolve` sends that name to the forwarded port:

```sh
kubectl -n ingress-system port-forward service/traefik 8000:80 >/dev/null &
curl --resolve cargo.local:8000:127.0.0.1 http://cargo.local:8000/
```

Wait a second for the port forward before `curl`. The reply must start with `app=cargo`. Traefik needs a few seconds to read the new access and the Ingress, so if you see `404` or a gateway error, wait and try again. Stop the port forward with `kill %1`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not add a second `--providers.kubernetesingress.ingressclass` argument. The check wants exactly one, with the value `traefik`.
>
> Do not grant `*` in `apiGroups` or `resources`, and do not add verbs other than `get`, `list` and `watch`. The check rejects a ClusterRole that grants more than read access.
>
> The rule must name the API group `discovery.k8s.io`. A rule for `endpointslices` in the core group `''` gives no access.
>
> Do not edit the Ingress `cargo`. The check expects its class `traefik`, its `web` entrypoint and its one rule unchanged.
