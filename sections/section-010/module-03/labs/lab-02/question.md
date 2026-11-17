---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Repair A Two-Entry Peer Rule

Solve this question on: `terminal`

The `starfleet-031-010-03-02` and `outpost-031-010-03-02` namespaces each run the `probe` Deployment (pods labelled `app: probe`, port 8080) with its `probe` Service, a `shuttle` pod labelled `app: shuttle` and a `drifter` pod. The `dock-031-010-03-02` namespace has a `shuttle` pod and a `telemetry` pod. Calico, the network plugin of this cluster, enforces NetworkPolicy.

The `shuttle` pod in `starfleet-031-010-03-02` must reach the `probe` pods in `outpost-031-010-03-02`. The policy `probe-from-starfleet` in `outpost-031-010-03-02` already selects the `probe` pods and allows TCP port 8080, but it lets in more pods than intended.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-03-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-03-02" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

Allow about 7 minutes for task work. Cluster startup adds time.

## Tasks

1. Read the NetworkPolicy `probe-from-starfleet` in `outpost-031-010-03-02` and find why it admits too many peers.
2. Repair `probe-from-starfleet` in place. After the repair it keeps the same name and the same pod selector, covers ingress only, and has one rule with one `from` entry. That entry holds a `namespaceSelector` for the namespace named `starfleet-031-010-03-02` (use the label `kubernetes.io/metadata.name`) and a `podSelector` for pods labelled `app: shuttle`, in the same entry. The rule allows TCP port 8080 only.
3. Prove the result. The `shuttle` pod in `starfleet-031-010-03-02` gets a response with `version=v1` from `http://probe.outpost-031-010-03-02/`. The `drifter` pod in `starfleet-031-010-03-02`, the `shuttle` pod in `outpost-031-010-03-02` and the `shuttle` pod in `dock-031-010-03-02` all time out when they request the same Service.

## Constraints

- Repair the existing policy. Do not create a second policy.
- Keep every Deployment and pod running and unchanged.

## How the answer is checked

The grader runs two checks. The first reads the NetworkPolicy `probe-from-starfleet` and needs the pod selector `app: probe`, the policy type `Ingress` only, and one rule with exactly one `from` entry that holds both the namespace name `starfleet-031-010-03-02` and the pod label `app: shuttle`, on TCP port 8080. The second sends a request to the `probe` Service in `outpost-031-010-03-02` from four pods: `shuttle` in `starfleet-031-010-03-02` must get `version=v1`, and `drifter` in `starfleet-031-010-03-02`, `shuttle` in `outpost-031-010-03-02` and `shuttle` in `dock-031-010-03-02` must each time out after 3 seconds. Both checks also need both `probe` Deployments fully rolled out and every client pod running and ready.

Hint: two entries in a `from` list are joined with OR, and one entry with two selectors is joined with AND.
