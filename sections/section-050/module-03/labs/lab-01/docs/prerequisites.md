---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Prerequisites

Use astrona, kubectl, Python 3, Podman and a shell. Node inspection exercises use the containers of this environment, not the physical host.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-03-01" || exit 1
CONTROL=astro-ats-031-lab-050-03-01-control-plane
WORKER=astro-ats-031-lab-050-03-01-worker
```

Keep this connection selected. Host-level commands name only the node containers of this environment.
