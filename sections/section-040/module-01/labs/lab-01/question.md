---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Block A Simulated Metadata Endpoint

Allow about 8 minutes for the tasks.

Separate permitted application dependencies from a metadata-style endpoint in the private network.

## Starting state

The isolated environment has two healthy probe replicas, an internal Service and two client Pods. The required result has not been configured.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-01-01" || exit 1
node_name="astro-ats-031-lab-040-01-01-control-plane"
worker_name="astro-ats-031-lab-040-01-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Required result

Create metadata-simulator as a healthy Python HTTP server with label app metadata-simulator on port 8080. Configure shuttle-isolation to allow only DNS and probe application traffic. A direct metadata-simulator request from shuttle must time out while an unrestricted drifter request proves that listener works. This models the network boundary; it does not claim to secure a cloud provider metadata service or host-network bypass.

## Verify The Result

The grader checks the required object fields and actual observations. Wait for controller convergence before submitting. Preserve the task's namespace, workload names and unrelated components.
