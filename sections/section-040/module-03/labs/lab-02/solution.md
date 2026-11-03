---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Find Pods That Expose The Runtime Or The Host Network Solution

## Find host path mounts

List the host paths of every pod in the three namespaces. The `grep` keeps lines that contain a host path:

```sh
for namespace in starfleet outpost dock; do
  kubectl -n "$namespace" get pods -o jsonpath='{range .items[*]}{.metadata.namespace}{"/"}{.metadata.name}{" "}{range .spec.volumes[*]}{.hostPath.path}{" "}{end}{"\n"}{end}'
done | grep -E ' /'
```

Three pods have host paths. `outpost/runtime-peek` mounts `/run/containerd/containerd.sock`, `starfleet/cri-helper` mounts the directory `/run/containerd`, which contains the socket, and `outpost/log-reader` mounts `/var/log`. Only the first two give access to the runtime.

## Find host network pods

```sh
for namespace in starfleet outpost dock; do
  kubectl -n "$namespace" get pods -o custom-columns='NAMESPACE:.metadata.namespace,NAME:.metadata.name,HOSTNETWORK:.spec.hostNetwork' --no-headers
done | grep true
```

One pod appears: `dock/net-tool`. The pod `fake-imds` also uses the host network, but it is in the namespace `metadata-stub`, which the task does not include.

## Record the result

The list holds three pods. Save it as `exposed-pods.txt`:

```text
dock/net-tool
outpost/runtime-peek
starfleet/cri-helper
```

Create the ConfigMap from the file:

```sh
kubectl -n dock create configmap exposed-pods --from-file=pods=exposed-pods.txt
```

Check what you stored:

```sh
kubectl -n dock get configmap exposed-pods -o jsonpath='{.data.pods}'
```

The output is the three lines. The pod `outpost/log-reader` is not in the list, because a log directory is not the runtime socket. All four pods must still be running.
After recording your result, remove the independent lab with `astrona destroy ats-031-lab-040-03-02`.
