---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Block The Metadata Address For A Namespace

Solve this question on: `terminal`

The cluster has the namespaces `starfleet-031-040-02-01`, `outpost-031-040-02-01` and `dock-031-040-02-01`, each with a `probe` Deployment and Service on port 80 and a client pod with the `curl` command. The pod `agent` in `starfleet-031-040-02-01` has the label `role=cloud-agent`. The namespace `metadata-stub-031-040-02-01` has the pod `fake-imds`, a fake metadata server on the host network of the worker node at `169.254.169.254` port 80, and a pod `control` that no policy selects. No NetworkPolicy exists.

The `drifter` pod in `outpost-031-040-02-01` runs a third-party image, and the security team wants it cut off from the cloud metadata address. The block must cover every pod in the namespace, present and future, and leave all other egress working.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-02-01" || exit 1
```

Keep this connection selected for the whole task.

Allow about 6 minutes for task work. Cluster startup adds time.

## Tasks

1. Confirm the starting state: `drifter` in `outpost-031-040-02-01` reaches `http://169.254.169.254/latest/meta-data/`.
2. Create a NetworkPolicy in `outpost-031-040-02-01` with an empty pod selector, so it applies to every pod in the namespace. It covers egress and blocks `169.254.169.254`, while all other egress stays allowed.
3. Prove the result. `drifter` must fail to reach the metadata address, and must still reach the `probe` Service in its own namespace by the name `probe`, and the `probe` Service in `starfleet-031-040-02-01` by its full DNS name `probe.starfleet-031-040-02-01.svc.cluster.local`.

## Constraints

- Do not change any other namespace. The pods in `starfleet-031-040-02-01` and the pod `control` must still reach the metadata address.
- Do not delete or recreate the existing pods.

## How the answer is checked

The grader runs two checks. The first sends a request from `drifter` to `http://169.254.169.254/latest/meta-data/`, which must fail to connect. The second lists the NetworkPolicies in `outpost-031-040-02-01` and needs one with an empty pod selector and `Egress` in its policy types. Both checks also need `drifter` running, HTTP status `200` from `drifter` to `http://probe/` and to `http://probe.starfleet-031-040-02-01.svc.cluster.local/`, and HTTP status `200` from `control` and from `shuttle` in `starfleet-031-040-02-01` to the metadata address.

Hint: an egress rule to `0.0.0.0/0` with `except` lists every address but the ones you want to block. Wait a few seconds after you apply a policy, because Calico needs a moment to program it.
