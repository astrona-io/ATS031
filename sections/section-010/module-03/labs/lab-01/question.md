---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow One Pod From Another Namespace

Solve this question on: `terminal`

The `starfleet-031-010-03-01` and `outpost-031-010-03-01` namespaces each run the `probe` Deployment (two pods labelled `app: probe`, port 8080), the `probe` Service (port 80), a `shuttle` pod labelled `app: shuttle` and a `drifter` pod. The `dock-031-010-03-01` namespace has a `shuttle` pod and a `telemetry` pod. No NetworkPolicy exists. Calico, the network plugin of this cluster, enforces policy.

The `shuttle` pod in `outpost-031-010-03-01` must reach the `probe` pods in `starfleet-031-010-03-01`. No other pod may reach them.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-03-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

Allow about 7 minutes for task work. Cluster startup adds time.

## Tasks

1. Look at the labels of the namespace `outpost-031-010-03-01` and of the pods in it, so you know which labels select the one allowed client.
2. Create the NetworkPolicy `probe-from-outpost` in `starfleet-031-010-03-01`. It selects the pods labelled `app: probe`, covers ingress only, and has one rule with one `from` entry. That entry holds a `namespaceSelector` for the namespace named `outpost-031-010-03-01` (use the label `kubernetes.io/metadata.name`) and a `podSelector` for pods labelled `app: shuttle`, in the same entry. The rule allows TCP port 8080 only.
3. Prove the result. The `shuttle` pod in `outpost-031-010-03-01` gets a response with `version=v1` from `http://probe.starfleet-031-010-03-01/`. The `drifter` pod in `outpost-031-010-03-01`, the `shuttle` pod in `dock-031-010-03-01` and the `shuttle` pod in `starfleet-031-010-03-01` all time out when they request the same Service.

## Constraints

- Create the policy in `starfleet-031-010-03-01` only. Do not change any other namespace.
- Keep every Deployment and pod running and unchanged.

## How the answer is checked

The grader runs two checks. The first reads the NetworkPolicy `probe-from-outpost` and needs the pod selector `app: probe`, the policy type `Ingress` only, and one rule with exactly one `from` entry that holds both the namespace name `outpost-031-010-03-01` and the pod label `app: shuttle`, on TCP port 8080. The second sends a request to the `probe` Service in `starfleet-031-010-03-01` from four pods: `shuttle` in `outpost-031-010-03-01` must get `version=v1`, and `drifter` in `outpost-031-010-03-01`, `shuttle` in `dock-031-010-03-01` and `shuttle` in `starfleet-031-010-03-01` must each time out after 3 seconds. Both checks also need both `probe` Deployments fully rolled out and every client pod running and ready.

Hint: Calico updates its rules a few seconds after you apply a policy. Repeat your test requests before you submit.
