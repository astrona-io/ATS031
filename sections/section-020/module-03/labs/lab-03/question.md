---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Recover A Broken Controller Manager Static Pod

Allow about 10 minutes for the tasks.

Someone edited the controller manager manifest on the `starfleet` control plane during the night shift. Since then, new pods of Deployments are no longer created. Bring the controller manager back.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-03-03` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The kube-controller-manager static pod fails to start after a manual edit of its manifest. A copy of the manifest from before the edit is in `/opt/training/backup/kube-controller-manager.yaml` on the control plane node.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-03-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-03-03" || exit 1
node_name="astro-ats-031-lab-020-03-03-control-plane"
worker_name="astro-ats-031-lab-020-03-03-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

- The kube-controller-manager process runs again on the control plane node, and the pod `kube-controller-manager-<node>` in `kube-system` is ready.
- The manifest `/etc/kubernetes/manifests/kube-controller-manager.yaml` has mode `600` or stricter and the owner `root:root`.
- `/etc/kubernetes/manifests` holds only the four manifests `etcd.yaml`, `kube-apiserver.yaml`, `kube-controller-manager.yaml` and `kube-scheduler.yaml`.
- The API server stays ready and both `probe` replicas stay available.

## Verify The Result

The grader reads the command line of the running `kube-controller-manager` process, the pod status, the file mode and the list of files in the manifests directory.
