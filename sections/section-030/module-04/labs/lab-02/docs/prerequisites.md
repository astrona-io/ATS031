---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Prerequisites

Use a host shell with astrona, kubectl and Python 3.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-04-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-04-02" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.
