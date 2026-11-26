# Close The Traefik API And Restrict Secret Reads — Solution

You solve this lab with two RBAC files and two JSON patches. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Read the Traefik arguments and ports, and ask the API server what the ServiceAccount `traefik` may read:

```sh
kubectl -n ingress-system get deployment traefik -o jsonpath='{.spec.template.spec.containers[0].args}'; echo
kubectl -n ingress-system get service traefik
kubectl get clusterrole traefik -o yaml
kubectl auth can-i get secrets -n kube-system --as=system:serviceaccount:ingress-system:traefik
```

Traefik runs with `--api.insecure=true`, which serves its API and dashboard without any login on port 8080, and the Service `traefik` publishes that port. The ClusterRole `traefik` lists `secrets`, so the last command prints `yes`: anyone who takes over the Traefik pod can read every Secret in the cluster.

## Step 2: limit Secret reads to one namespace (check `secret-rbac`)

Role-based access control (RBAC) gives permissions with Roles and binds them to users or ServiceAccounts. A ClusterRole with a ClusterRoleBinding applies in every namespace; a Role with a RoleBinding applies only in its own namespace. Traefik needs Secrets only in `starfleet-031-030-04-04`, so the Secret permission moves into a Role there.

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

Then remove `secrets` from the ClusterRole. Save this as `clusterrole-traefik.yaml`:

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

## Step 3: remove port 8080 from the Service (check `api-closed`)

The Service `traefik` lists three ports: `web` (80), `websecure` (443) and `dashboard` (8080). A JSON patch changes one field of an object by its path. The `test` operation makes the patch stop if the third port is not 8080, so you cannot remove the wrong port by mistake.

Save this as `traefik-service-patch.json`:

```json
[
  {"op": "test", "path": "/spec/ports/2/port", "value": 8080},
  {"op": "remove", "path": "/spec/ports/2"}
]
```

Apply it:

```sh
kubectl -n ingress-system patch service traefik --type=json --patch-file traefik-service-patch.json
```

The check `api-closed` also needs the Deployment change in the next step.

## Step 4: close the API and watch one namespace (checks `api-closed` and `secret-scope`)

In the Deployment, the seventh argument (index 6) is `--api.insecure=true` and the third port (index 2) is 8080. The patch replaces that argument with `--providers.kubernetesingress.namespaces=starfleet-031-030-04-04` and removes the port. With this argument, the Traefik Ingress provider watches Ingress objects and their Secrets only in that namespace, so it no longer needs to read Secrets anywhere else.

Save this as `traefik-deployment-patch.json`:

```json
[
  {"op": "test", "path": "/spec/template/spec/containers/0/args/6", "value": "--api.insecure=true"},
  {"op": "replace", "path": "/spec/template/spec/containers/0/args/6", "value": "--providers.kubernetesingress.namespaces=starfleet-031-030-04-04"},
  {"op": "test", "path": "/spec/template/spec/containers/0/ports/2/containerPort", "value": 8080},
  {"op": "remove", "path": "/spec/template/spec/containers/0/ports/2"}
]
```

Apply it and wait for the new Traefik pod:

```sh
kubectl -n ingress-system patch deployment traefik --type=json --patch-file traefik-deployment-patch.json
kubectl -n ingress-system rollout status deployment/traefik --timeout=180s
```

## Step 5: test the permissions and the route (all checks)

Ask the API server again:

```sh
kubectl auth can-i get secrets -n kube-system --as=system:serviceaccount:ingress-system:traefik
kubectl auth can-i list secrets --all-namespaces --as=system:serviceaccount:ingress-system:traefik
kubectl auth can-i watch secrets -n starfleet-031-030-04-04 --as=system:serviceaccount:ingress-system:traefik
kubectl -n ingress-system get service traefik
```

The first two commands must print `no` and the third `yes`. The Service must list only the ports 80 and 443.

Start a port forward to the Traefik HTTPS port in another terminal:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443
```

Then send a request that trusts only the `dock-tls` certificate:

```sh
kubectl -n starfleet-031-030-04-04 get secret dock-tls -o jsonpath='{.data.tls\.crt}' | base64 -d > dock.crt
curl --cacert dock.crt --resolve dock.example.test:8443:127.0.0.1 https://dock.example.test:8443/
```

It must print a line that starts with `app=dock`. Stop the port forward with Ctrl+C.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Removing `secrets` from the ClusterRole without the Role and RoleBinding in `starfleet-031-030-04-04` leaves Traefik unable to read `dock-tls`. It then serves its default certificate, and the check for `https://dock.example.test` fails.
>
> Removing only the argument `--api.insecure=true` is not enough. The check also rejects the container port 8080 in the Deployment and the port 8080 in the Service.
>
> Any argument that starts with `--api.insecure` and does not end with `=false` fails the check. Remove the argument rather than leave a copy of it.
>
> Write the namespace argument exactly as `--providers.kubernetesingress.namespaces=starfleet-031-030-04-04`. The check looks for this exact argument.
