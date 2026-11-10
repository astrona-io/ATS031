---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Block The Metadata Address For A Namespace

Allow about 6 minutes for the tasks.

Block the cloud metadata address for every pod in one namespace and keep all other egress working.

## Starting state

The cluster has the namespaces `starfleet-031-040-02-01`, `outpost-031-040-02-01` and `dock-031-040-02-01`, each with a `probe` Deployment and Service on port 80 and a client pod with the `curl` command. The pod `agent` in `starfleet-031-040-02-01` has the label `role=cloud-agent`. The namespace `metadata-stub-031-040-02-01` has the pod `fake-imds`, a fake metadata server on the host network of the worker node at `169.254.169.254` port 80, and a pod `control` that no policy selects. No NetworkPolicy exists.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-02-01" || exit 1
```

Keep this connection selected for the whole task.

## Required result

The `drifter` pod in `outpost-031-040-02-01` runs a third-party image, and the security team wants it cut off from the cloud metadata address. Create a NetworkPolicy in `outpost-031-040-02-01` that applies to every pod in the namespace, present and future, and blocks egress to `169.254.169.254`. Other egress must keep working: `drifter` must still reach the `probe` Service in `outpost-031-040-02-01` by its name `probe`, and the `probe` Service in `starfleet-031-040-02-01` by its full DNS name. Do not change any other namespace. The pods in `starfleet-031-040-02-01` must still reach the metadata address, and the pod `control` must still reach it too.

## Verify the result

The grader sends live requests from the client pods and reads the objects. Wait a few seconds after you apply a policy, because the network plugin needs a moment to program it. Do not delete or recreate the existing pods unless the task says so.
