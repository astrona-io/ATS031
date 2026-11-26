# Turn On NodeRestriction And Remove A Protected Node Label

The kube-apiserver runs without the `NodeRestriction` admission plugin, so the kubelet credential of the worker node `astro-ats-031-lab-040-03-05-worker` can set any label on its own node. It has already given itself the label `node-restriction.kubernetes.io/dedicated=payments`. The API server manifest is `/etc/kubernetes/manifests/kube-apiserver.yaml` on the node `astro-ats-031-lab-040-03-05-control-plane`.

1. Make the running kube-apiserver use `NodeRestriction` in `--enable-admission-plugins`, with `Node` and `RBAC` still in `--authorization-mode`.
2. The worker kubelet credential `/etc/kubernetes/kubelet.conf` is refused when it sets a `node-restriction.kubernetes.io/` label or `node-role.kubernetes.io/control-plane` on its own node.
3. Remove the label `node-restriction.kubernetes.io/dedicated` from the worker node, and keep the node `Ready`.

Leave no backup copy of the API server manifest in `/etc/kubernetes/manifests`, and do not use `AlwaysAllow` authorization.
