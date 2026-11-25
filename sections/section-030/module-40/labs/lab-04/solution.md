---
exam_objectives:
- Properly set up Ingress with TLS
---
# Close The Traefik API And Restrict Secret Reads Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-04-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-04-04" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Inspect the current exposure

```sh
kubectl auth can-i list secrets --all-namespaces --as=system:serviceaccount:ingress-system:traefik
kubectl -n ingress-system get deployment traefik -o jsonpath='{range .spec.template.spec.containers[0].args[*]}{@}{"\n"}{end}'
kubectl -n ingress-system get service traefik -o jsonpath='{range .spec.ports[*]}{.name} {.port}{"\n"}{end}'
```

The first command answers `yes`. The seventh argument is `--api.insecure=true`, and the Service publishes `dashboard 8080`.

## Allow Secrets in one namespace only

Save this as `role-traefik-secrets.yaml`:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: traefik-secrets
  namespace: starfleet-031-030-04-04
rules:
- apiGroups:
  - ''
  resources:
  - secrets
  verbs:
  - get
  - list
  - watch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: traefik-secrets
  namespace: starfleet-031-030-04-04
subjects:
- kind: ServiceAccount
  name: traefik
  namespace: ingress-system
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: traefik-secrets
```

Apply it:

```sh
kubectl apply -f role-traefik-secrets.yaml
```

Save this as `clusterrole-traefik.yaml`. It is the old ClusterRole without `secrets`:

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

## Close the API port

Remove the port from the Service first. The `test` operations make each patch fail if the item at that position is not the one you expect. Save this as `traefik-service-patch.json`:

```json
[
  {"op": "test", "path": "/spec/ports/2/port", "value": 8080},
  {"op": "remove", "path": "/spec/ports/2"}
]
```

Save this as `traefik-deployment-patch.json`. It replaces `--api.insecure=true` with the namespaces argument and removes the container port:

```json
[
  {"op": "test", "path": "/spec/template/spec/containers/0/args/6", "value": "--api.insecure=true"},
  {"op": "replace", "path": "/spec/template/spec/containers/0/args/6", "value": "--providers.kubernetesingress.namespaces=starfleet-031-030-04-04"},
  {"op": "test", "path": "/spec/template/spec/containers/0/ports/2/containerPort", "value": 8080},
  {"op": "remove", "path": "/spec/template/spec/containers/0/ports/2"}
]
```

Apply both and wait for the new pod:

```sh
kubectl -n ingress-system patch service traefik --type=json --patch-file traefik-service-patch.json
kubectl -n ingress-system patch deployment traefik --type=json --patch-file traefik-deployment-patch.json
kubectl -n ingress-system rollout status deployment/traefik
```

## Verify

```sh
kubectl auth can-i list secrets --all-namespaces --as=system:serviceaccount:ingress-system:traefik
kubectl auth can-i list secrets -n starfleet-031-030-04-04 --as=system:serviceaccount:ingress-system:traefik
kubectl -n ingress-system logs deployment/traefik --tail=20
```

The first command answers `no` and the second `yes`. The log has no new `forbidden` errors. Without the namespaces argument, Traefik would still try to watch Secrets in every namespace and log errors.

## Common pitfalls

> [!WARNING]
> - **Removing `secrets` without the namespaces argument.** Traefik keeps watching Secrets in every namespace, and those requests are now forbidden.
> - **Closing the Service port but leaving `--api.insecure=true`.** Any pod can still reach the API on the pod address.
> - **Granting the Role to the wrong ServiceAccount.** The subject is `traefik` in `ingress-system`, not a ServiceAccount in the lab namespace.

## Clean up

Destroy the lab cluster when you are done:

```sh
astrona destroy ats-031-lab-030-04-04
```
