---
exam_objectives:
- Protect node metadata and endpoints
---
# Prerequisites

Use `astrona`, `kubectl` and a shell with Podman or Docker. Select the private kubeconfig of this independent `kind` environment. A kubeconfig identifies the cluster and credentials that `kubectl`, the Kubernetes command-line tool, uses.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-03-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-03-05" || exit 1
```

Keep this connection selected. The cluster has one control plane node and one worker node. Each node is a container on your machine, and node commands run inside those containers, not on your own computer.
