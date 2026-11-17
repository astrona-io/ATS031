---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow One Peer And Deny Another

Solve this question on: `terminal`

The namespace `starfleet-031-010-01-01` runs the `probe` Deployment (two pods labelled `app: probe`, port 8080) behind the Service `probe`, and the client pod `shuttle` labelled `app: shuttle`. The namespace `outpost-031-010-01-01` runs the client pod `drifter`. Calico, the network plugin of this cluster, enforces NetworkPolicy. No policy exists yet, so every pod can reach `probe`.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-01-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

Allow about 6 minutes for task work. Cluster startup adds time.

## Tasks

1. Look at the labels of the pods in `starfleet-031-010-01-01` and `outpost-031-010-01-01`, so you know which label each client has.
2. Create the NetworkPolicy `probe-shuttle` in `starfleet-031-010-01-01`. It selects the pods labelled `app: probe`, covers ingress only, and allows pods labelled `app: shuttle` from the same namespace on TCP port 8080 only.
3. Prove the result. `shuttle` must get a response with `version=v1` from `http://probe/`, and a request from `drifter` to `http://probe.starfleet-031-010-01-01/` must time out.

## Constraints

- Keep the `probe` Deployment, the `shuttle` pod and the `drifter` pod running and unchanged.
- Do not create any other policy that also allows `drifter`.

## How the answer is checked

The grader runs two checks. The first reads the NetworkPolicy `probe-shuttle` and needs the pod selector `app: probe`, the policy type `Ingress` only, and one rule that allows `app: shuttle` on TCP port 8080. The second sends a request from `shuttle` to the Service `probe`, which must contain `version=v1`, and a request from `drifter`, which must time out. Both checks also need the `probe` Deployment fully rolled out and both client pods running and ready.

Hint: Calico updates its rules a few seconds after you apply a policy. Repeat your test requests before you submit.
