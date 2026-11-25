---
exam_objectives:
- Protect node metadata and endpoints
---
# Find Host-Network Pods And Block New Ones Solution

## Find the pods

Print each pod of the two namespaces with its `hostNetwork` and `privileged` fields:

```sh
kubectl get pods -n dock-031-040-03-04 -o custom-columns='NAME:.metadata.name,HOSTNETWORK:.spec.hostNetwork,PRIVILEGED:.spec.containers[*].securityContext.privileged'
kubectl get pods -n outpost-031-040-03-04 -o custom-columns='NAME:.metadata.name,HOSTNETWORK:.spec.hostNetwork,PRIVILEGED:.spec.containers[*].securityContext.privileged'
```

The `HOSTNETWORK` column shows `true` for `net-tool` and `port-watch` in `dock-031-040-03-04` and for `sniffer` in `outpost-031-040-03-04`. It shows `<none>` for the other pods, because the field is not set. The pod `debug-shell` shows `true` only in the `PRIVILEGED` column. A privileged pod keeps its pod interface, so it does not belong on this list.

## Record the list

Save the three lines in a file and create the ConfigMap from it:

```sh
printf 'dock-031-040-03-04/net-tool\ndock-031-040-03-04/port-watch\noutpost-031-040-03-04/sniffer\n' > host-network-pods.txt
kubectl -n dock-031-040-03-04 create configmap host-network-pods --from-file=pods=host-network-pods.txt
kubectl -n dock-031-040-03-04 get configmap host-network-pods -o jsonpath='{.data.pods}'
```

The last command prints the three lines back.

## Enforce the baseline level

Pod Security admission reads the label `pod-security.kubernetes.io/enforce` on a namespace. The `baseline` level forbids `hostNetwork`, `hostPID`, `hostIPC`, host path volumes and privileged containers. A server-side dry run first shows what the label would report, without changing anything:

```sh
kubectl label --dry-run=server --overwrite namespace dock-031-040-03-04 pod-security.kubernetes.io/enforce=baseline
kubectl label --overwrite namespace dock-031-040-03-04 pod-security.kubernetes.io/enforce=baseline
```

Both commands print warnings for `net-tool` and `port-watch`, because they already break the level. Pod Security admission checks a pod only when it is created, so the two existing pods keep running. That is what the review needs.

## Verify

Send a host-network pod and an ordinary pod to the API server as a dry run:

```sh
kubectl -n dock-031-040-03-04 run hn-check --image=docker.io/curlimages/curl:8.11.1 --dry-run=server --overrides='{"apiVersion":"v1","spec":{"hostNetwork":true}}' -- sleep 60
kubectl -n dock-031-040-03-04 run plain-check --image=docker.io/curlimages/curl:8.11.1 --dry-run=server -- sleep 60
```

The API server rejects the first pod with a `forbidden` error that names `hostNetwork`. It accepts the second one and prints `pod/plain-check created (server dry run)`.

After recording your result, remove the independent lab with `astrona destroy ats-031-lab-040-03-04`.

## Common pitfalls

> [!WARNING]
> Adding `debug-shell` to the list mixes up two settings: a privileged pod still uses the pod network. Using the `restricted` level instead of `baseline` also rejects ordinary pods that do not set a `securityContext`. A `warn` or `audit` label only reports a pod; only the `enforce` label makes the API server reject it.
