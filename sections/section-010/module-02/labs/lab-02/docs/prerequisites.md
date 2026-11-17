---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Prerequisites

Use a host shell with astrona, kubectl and Python 3.

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-02-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-02-02" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.
