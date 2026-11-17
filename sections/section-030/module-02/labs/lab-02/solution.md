---
exam_objectives:
- Properly set up Ingress with TLS
---
# Repair The Traefik Installation Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-02-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-02-02" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Read the installation

Start with the arguments, the class and the permissions of the ServiceAccount:

```sh
kubectl -n ingress-system get deployment traefik -o jsonpath='{range .spec.template.spec.containers[0].args[*]}{@}{"\n"}{end}'
kubectl get ingressclass traefik -o jsonpath='{.spec.controller}{"\n"}'
kubectl auth can-i list endpointslices.discovery.k8s.io --all-namespaces --as=system:serviceaccount:ingress-system:traefik
kubectl -n ingress-system logs deployment/traefik --tail=20
```

The second argument names the class `traefik-internal`, so Traefik ignores every Ingress of the class `traefik`. The `auth can-i` command answers `no`. Traefik reads EndpointSlices to find the pod addresses behind a Service, and the log shows the forbidden requests.

## Fix the ClusterRole

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

## Fix the class argument

The `args` list is not merged by key, so a merge patch would replace the whole list. A JSON patch changes one item. The `test` operation makes the patch fail if the second item is not the value you expect. Save this as `traefik-class-patch.json`:

```json
[
  {"op": "test", "path": "/spec/template/spec/containers/0/args/1", "value": "--providers.kubernetesingress.ingressclass=traefik-internal"},
  {"op": "replace", "path": "/spec/template/spec/containers/0/args/1", "value": "--providers.kubernetesingress.ingressclass=traefik"}
]
```

Apply it and wait for the new pod. The new pod also starts with the new permissions:

```sh
kubectl -n ingress-system patch deployment traefik --type=json --patch-file traefik-class-patch.json
kubectl -n ingress-system rollout status deployment/traefik
```

Then check the result. Open a port forward in a second terminal and send a request:

```sh
kubectl -n ingress-system port-forward service/traefik 8080:80
curl -s -H 'Host: cargo.local' http://127.0.0.1:8080/
```

The response starts with `app=cargo`.

## Common pitfalls

> [!WARNING]
> - **Giving the controller `create` or `update` verbs to make the errors go away.** Traefik only reads objects. Grant `get`, `list` and `watch` and nothing more.
> - **Patching `args` with a merge patch.** It replaces the whole list. Use a JSON patch that changes one item.
> - **Renaming the IngressClass instead of the argument.** The Ingress objects of the cluster name `traefik`, so the controller must watch that class.

## Clean up

Destroy the lab cluster when you are done:

```sh
astrona destroy ats-031-lab-030-02-02
```
