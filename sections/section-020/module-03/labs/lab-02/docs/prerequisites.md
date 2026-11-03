---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Prerequisites

Use astrona, kubectl, Python 3, Podman and a shell. Node inspection exercises use the containers in this environment, not the physical host.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-03-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-03-02" || exit 1
node_name="astro-ats-031-lab-020-03-02-control-plane"
worker_name="astro-ats-031-lab-020-03-02-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.
