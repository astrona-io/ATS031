---
exam_objectives:
- Protect node metadata and endpoints
---
# Turn On NodeRestriction And Remove A Protected Node Label

Allow about 10 minutes for the tasks.

A review of the `starfleet` cluster found that the worker node gave itself the label `node-restriction.kubernetes.io/dedicated=payments`. Workloads that select this label would be scheduled onto that node. A kubelet must never be able to set that label, so the API server is missing a control.

## Starting state

The cluster has one control plane node and one worker node. The kubelet is the agent on each node that starts the pods. It talks to the API server with its own credential, the kubeconfig file `/etc/kubernetes/kubelet.conf` on its node. The API server runs as a static pod: the kubelet on the control plane node starts it from the file `/etc/kubernetes/manifests/kube-apiserver.yaml`. The `NodeRestriction` admission plugin was removed from that manifest. While it was off, the worker kubelet's credential set the protected label on the worker node. The namespace `starfleet-031-040-03-05` exists and is empty.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-03-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-03-05" || exit 1
```

Keep this connection selected for the whole task. The nodes are containers named `astro-ats-031-lab-040-03-05-control-plane` and `astro-ats-031-lab-040-03-05-worker`. Open a shell on a node with `podman exec -it <container name> bash`, or with `docker` if your machine uses Docker.

## Required result

- The kube-apiserver static pod runs with `NodeRestriction` in `--enable-admission-plugins`, and `--authorization-mode` still contains `Node` and `RBAC`.
- The worker kubelet's own credential can no longer set a label with the prefix `node-restriction.kubernetes.io/` or the label `node-role.kubernetes.io/control-plane` on the worker node.
- The worker node no longer carries the label `node-restriction.kubernetes.io/dedicated`, and it is `Ready`.

Do not edit the manifest inside `/etc/kubernetes/manifests` in place, and do not leave a backup copy in that directory: the kubelet starts every file there.

## Verify the result

The grader reads the command of the kube-apiserver pod. It then runs `kubectl` on the worker node with the kubelet's kubeconfig file and sends both label writes to the worker node as server-side dry runs (`--dry-run=server`). The API server runs its admission plugins for a dry run but does not store the change. Both writes must be refused with a `Forbidden` error. The API server restarts after a manifest change, so wait until `kubectl` answers again before you check.
