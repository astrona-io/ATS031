# Find Host-Network Pods And Block New Ones — Solution

You solve this lab by reading one pod field, recording the result in a ConfigMap and adding one label to the namespace. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Print each pod of the two namespaces with its `hostNetwork` and `privileged` fields:

```sh
kubectl get pods -n dock-031-040-03-04 -o custom-columns='NAME:.metadata.name,HOSTNETWORK:.spec.hostNetwork,PRIVILEGED:.spec.containers[*].securityContext.privileged'
kubectl get pods -n outpost-031-040-03-04 -o custom-columns='NAME:.metadata.name,HOSTNETWORK:.spec.hostNetwork,PRIVILEGED:.spec.containers[*].securityContext.privileged'
kubectl get namespace dock-031-040-03-04 --show-labels
```

The `HOSTNETWORK` column shows `true` for `net-tool` and `port-watch` in `dock-031-040-03-04` and for `sniffer` in `outpost-031-040-03-04`. It shows `<none>` for the other pods, because the field is not set. The pod `debug-shell` shows `true` only in the `PRIVILEGED` column. A privileged pod keeps its pod interface, so it does not belong on the list. The namespace has no `pod-security.kubernetes.io` label yet.

## Step 2: record the list (check `host-network-listed`)

Write the three pods into the key `pods`, one per line. The `|` keeps the line breaks in the value.

Save this as `configmap-host-network-pods.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: host-network-pods
  namespace: dock-031-040-03-04
data:
  pods: |
    dock-031-040-03-04/net-tool
    dock-031-040-03-04/port-watch
    outpost-031-040-03-04/sniffer
```

Apply it, then read the value back:

```sh
kubectl apply -f configmap-host-network-pods.yaml
kubectl -n dock-031-040-03-04 get configmap host-network-pods -o jsonpath='{.data.pods}'
```

The last command prints the three lines.

## Step 3: enforce the baseline level (check `admission-blocks-host-network`)

Pod Security admission reads the label `pod-security.kubernetes.io/enforce` on a namespace. The `baseline` level forbids `hostNetwork`, `hostPID`, `hostIPC`, host path volumes and privileged containers. A server-side dry run first shows what the label would report, without changing anything:

```sh
kubectl label --dry-run=server --overwrite namespace dock-031-040-03-04 pod-security.kubernetes.io/enforce=baseline
kubectl label --overwrite namespace dock-031-040-03-04 pod-security.kubernetes.io/enforce=baseline
```

Both commands print warnings for `net-tool` and `port-watch`, because they already break the level. Pod Security admission checks a pod only when it is created, so the two existing pods keep running. Send a host-network pod to the API server as a dry run:

```sh
kubectl -n dock-031-040-03-04 run hn-check --image=docker.io/curlimages/curl:8.11.1 --dry-run=server --overrides='{"apiVersion":"v1","spec":{"hostNetwork":true}}' -- sleep 60
```

The API server rejects the pod with a `forbidden` error that names `hostNetwork`.

## Step 4: confirm ordinary pods still start (check `plain-pod-accepted`)

`baseline` forbids only the known ways out of the pod. It does not require a `securityContext`, so an ordinary pod passes:

```sh
kubectl -n dock-031-040-03-04 run plain-check --image=docker.io/curlimages/curl:8.11.1 --dry-run=server -- sleep 60
```

The API server accepts the pod and prints `pod/plain-check created (server dry run)`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Adding `debug-shell` to the list mixes up two settings: a privileged pod still uses the pod network. The checks reject any extra line, any duplicate line and any key other than `pods`.
>
> Using the `restricted` level instead of `baseline` also rejects ordinary pods that do not set a `securityContext`. A `warn` or `audit` label only reports a pod; only the `enforce` label makes the API server reject it.
>
> Do not delete or recreate `net-tool`, `port-watch` or `sniffer` to clear the warnings. The checks need every starting pod running with its original `hostNetwork` value.
