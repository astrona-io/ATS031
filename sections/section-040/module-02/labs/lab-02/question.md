---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Allow The Metadata Address For One Labelled Pod

Solve this question on: `terminal`

The cluster has the namespaces `starfleet-031-040-02-02`, `outpost-031-040-02-02` and `dock-031-040-02-02`, each with a `probe` Deployment and Service on port 80 and a client pod with the `curl` command. The pod `agent` in `starfleet-031-040-02-02` has the label `role=cloud-agent`. The namespace `metadata-stub-031-040-02-02` has the pod `fake-imds`, a fake metadata server on the host network of the worker node at `169.254.169.254` port 80, and a pod `control` that no policy selects. No NetworkPolicy exists.

The pod `agent` in `starfleet-031-040-02-02` needs the metadata address to do its work. The pod `shuttle` in the same namespace does not.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-02-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-02-02" || exit 1
```

Keep this connection selected for the whole task.

Allow about 8 minutes for task work. Cluster startup adds time.

## Tasks

1. Look at the labels of `agent` and `shuttle` in `starfleet-031-040-02-02`, and confirm that both reach `http://169.254.169.254/latest/meta-data/` now.
2. Configure NetworkPolicy in `starfleet-031-040-02-02` so that the pods of the namespace cannot reach `169.254.169.254`, while pods with the existing label `role=cloud-agent` can still reach it on port 80.
3. Prove the result. `agent` must reach the metadata address, `shuttle` must not, and both pods must still reach the `probe` Service by its name `probe`.

## Constraints

- Use the existing label. Do not add or remove labels, and do not delete pods.
- Do not change other namespaces: `drifter` in `outpost-031-040-02-02` must still reach the metadata address.

## How the answer is checked

The grader runs one check. It sends a request from `shuttle` to `http://169.254.169.254/latest/meta-data/`, which must fail to connect. The check also needs `agent` to keep the label `role=cloud-agent`, `shuttle` to have no `role` label, HTTP status `200` from `agent` to the metadata address, HTTP status `200` from both `agent` and `shuttle` to `http://probe/`, and HTTP status `200` from `drifter` in `outpost-031-040-02-02` to the metadata address.

Hint: NetworkPolicies add up. A pod that any policy allows to reach an address can reach it, so a second policy that selects only `role=cloud-agent` can open the address again for `agent`. Wait a few seconds after you apply a policy, because Calico needs a moment to program it.
