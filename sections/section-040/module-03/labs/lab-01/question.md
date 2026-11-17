---
exam_objectives:
- Protect node metadata and endpoints
---
# Close The Kubelet Read-Only Port

Allow about 8 minutes for the tasks.

A security scan reports that the worker node of this cluster answers on port 10255 without a credential. Close that port on the node itself.

## Starting state

The cluster has one control plane node and one worker node. The kubelet is the agent on each node that starts the pods. The kubelet on the worker reads its settings from the file `/var/lib/kubelet/config.yaml`, and that file sets `readOnlyPort: 10255`. The namespace `dock-031-040-03-01` has a pod `inspector` with the `curl` command.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-03-01" || exit 1
```

Keep this connection selected for the whole task. The worker node is a container named `astro-ats-031-lab-040-03-01-worker`. Open a shell on it with `podman exec -it astro-ats-031-lab-040-03-01-worker bash`, or with `docker` if your machine uses Docker.

## Required result

- The file `/var/lib/kubelet/config.yaml` on the worker sets `readOnlyPort: 0` or has no `readOnlyPort` line.
- The running kubelet on the worker uses the new setting, and port 10255 on the worker no longer answers.
- The kubelet still serves its HTTPS port 10250, and the worker node is `Ready`.

Do not change the control plane node and do not create a NetworkPolicy: the port must be closed in the kubelet, not only blocked on the network path.

## Verify the result

The grader reads the file on the worker and the running kubelet configuration through the API server. It sends requests from `inspector` to port 10255 and port 10250 on the worker.
