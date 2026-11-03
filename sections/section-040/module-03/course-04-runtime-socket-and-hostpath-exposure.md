---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Runtime Socket And hostPath Exposure

The container runtime on a node, containerd in this cluster, listens on a Unix socket. A Unix socket is a file that programs use to talk to a local service. Whoever can open the socket can ask the runtime to create, inspect and stop containers on the node. This part shows how a pod gets the socket, finds every pod that has it, and explains how to stop it.

## How a pod gets the socket

A `hostPath` volume mounts a file or a directory of the node into a container. If the path is the runtime socket, `/run/containerd/containerd.sock`, the container sees the socket as a file. If the path is the directory `/run/containerd`, the container sees the socket inside it, so a directory mount is as dangerous as a mount of the socket itself. A process in the container that runs as root can then talk to the runtime. It can start a new privileged container that mounts the whole file system of the node, and from there it controls the node and every other container on it. The Kubernetes API, RBAC and NetworkPolicy do not see these actions, because the pod uses a local file and not the network.

Some tools do need the socket, such as node agents that report container metrics and image builders. The rule is that a mount must be justified, narrow and limited to system namespaces. In an application namespace it is a finding.

## Find every pod that has a host path

<!-- astrona:playground:renew -->

You do not need `jq`. A JSONPath expression prints the namespace and name of each pod together with the host paths of its volumes. Pods without a host path print an empty second column, so the command keeps only lines that contain a slash after the pod name:

```sh
kubectl get pods -A -o jsonpath='{range .items[*]}{.metadata.namespace}{"/"}{.metadata.name}{" "}{range .spec.volumes[*]}{.hostPath.path}{" "}{end}{"\n"}{end}' | grep -E ' /'
```

Expect system pods in `kube-system` and the network plugin namespaces, because node agents need the host. The application namespaces also show `outpost/runtime-peek` with the socket path, `starfleet/cri-helper` with the directory `/run/containerd`, and `outpost/log-reader` with `/var/log`. The last one is not a runtime exposure, but a log directory can hold sensitive data, so it still needs a reason. Narrow the search to the runtime by filtering for the word `containerd`:

```sh
kubectl get pods -A -o jsonpath='{range .items[*]}{.metadata.namespace}{"/"}{.metadata.name}{" "}{range .spec.volumes[*]}{.hostPath.path}{" "}{end}{"\n"}{end}' | grep -E 'containerd|docker.sock|crio'
```

The filter finds the two pods that expose the runtime, and it also finds system pods that mount the same path for a reason. The names `docker.sock` and `crio` cover other runtimes, so the same command works when you do not know which runtime a cluster uses.

## See what the pod holds

Look at the socket from inside `runtime-peek`. The pod runs as root, as a pod that uses the socket usually does:

```sh
kubectl -n outpost exec runtime-peek -- id
kubectl -n outpost exec runtime-peek -- ls -l /run/containerd/containerd.sock
```

The first command shows user id 0. The second shows a file whose type letter is `s`, which marks a socket, owned by root. The playground does not call the runtime from the pod. With a client such as `ctr` or `crictl` in the image, the same pod could list every container on the node, read the environment of other pods and start a new container.

## How to stop it

There are three layers. First, review: list host paths regularly, as above, and refuse a socket mount that has no owner. Second, admission: a policy engine or the built-in Pod Security admission can reject pods that use `hostPath`. The `baseline` level of the Pod Security Standards forbids host path volumes and the host network. A server-side dry run shows what the level would reject without changing anything:

```sh
kubectl label --dry-run=server --overwrite namespace outpost pod-security.kubernetes.io/enforce=baseline
```

The response is a warning that existing pods in `outpost` violate the level, and it names the pods and the reason, such as a host path volume. The label is not stored, because of the dry run. Third, runtime hardening: the pod should not run as root, should drop capabilities and should use a read-only root file system, so that a mount alone is not enough. Admission control and pod hardening are the subject of other parts of the exam, and this part names only what is needed here.

Network policy plays no role against a socket, because the socket is not on the network. That is why this exposure needs its own search. The next part looks at the pods that bypass the pod network instead.

## Common pitfalls

> [!WARNING]
> - **Searching only for `containerd.sock`.** A mount of the parent directory `/run/containerd` exposes the same socket.
> - **Forgetting other runtimes.** The path can be `docker.sock` or a CRI-O socket.
> - **Mounting the socket read-only and calling it safe.** A read-only bind mount does not stop a client from writing requests to the socket.
> - **Ignoring system namespaces completely.** A pod in `kube-system` that has a socket mount for no reason is also a finding.
