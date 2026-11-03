---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Prerequisites

Use `astrona`, `kubectl` and a shell. Select the private kubeconfig of this independent `kind` environment. A kubeconfig identifies the cluster and credentials that `kubectl`, the Kubernetes command-line tool, uses.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-02-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-02-02" || exit 1
```

Keep this connection selected. The cluster has one control plane node and one worker node, and Calico enforces NetworkPolicy.
