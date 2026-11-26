# Recover A Broken Controller Manager Static Pod

Someone edited the controller manager manifest during the night shift. Since then, new pods of Deployments are no longer created. A copy of the manifest from before the edit is in `/opt/training/backup/kube-controller-manager.yaml` on the control plane node.

1. Remove the fault from `/etc/kubernetes/manifests/kube-controller-manager.yaml`.
2. The kube-controller-manager process runs again, and the pod `kube-controller-manager-<node>` in `kube-system` is ready.
3. The manifest has mode `600` or stricter and the owner `root:root`, and `/etc/kubernetes/manifests` holds only `etcd.yaml`, `kube-apiserver.yaml`, `kube-controller-manager.yaml` and `kube-scheduler.yaml`.

Node files belong to root; use `sudo`. The API server must stay ready and both `probe` replicas in `starfleet-031-020-03-03` must stay available.
