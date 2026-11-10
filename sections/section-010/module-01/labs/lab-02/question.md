---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow DNS And One Application Dependency

Solve this question on: `terminal`

The namespace `starfleet-031-010-01-02` runs the `probe` Deployment (two pods labelled `app: probe`, port 8080) behind the Service `probe`, and the client pod `shuttle` labelled `app: shuttle`. The namespace `outpost-031-010-01-02` runs the pod `drifter`, which no policy restricts. Calico, the network plugin of this cluster, enforces NetworkPolicy. No policy exists yet, so `shuttle` can send traffic anywhere. The team wants `shuttle` to reach only name resolution (DNS, the Domain Name System) and `probe`, and wants proof that it cannot reach a healthy server that it has no reason to call.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-01-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-01-02" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

Allow about 8 minutes for task work. Cluster startup adds time.

## Tasks

1. Create the NetworkPolicy `shuttle-egress` in `starfleet-031-010-01-02`. It selects the pods labelled `app: shuttle` and covers egress only. One rule allows DNS on UDP and TCP port 53, only to the pods labelled `k8s-app: kube-dns` in the namespace `kube-system` (selected by the label `kubernetes.io/metadata.name`, in the same peer entry). A second rule allows TCP port 8080, only to pods labelled `app: probe` in the same namespace.
2. Create the pod `blocked-server` in `starfleet-031-010-01-02` with the label `app: blocked-server` and `restartPolicy: Never`. Its one container is named `web`, uses the image `docker.io/library/python:3.13-alpine` and runs the command `python -m http.server 8080`. Wait until it is ready.
3. Prove the result. From `shuttle`, `nslookup probe.starfleet-031-010-01-02.svc.cluster.local` must return an address, and `http://probe/` must return a response with `version=v1`. A request from `shuttle` to the `blocked-server` pod address on port 8080 must time out.

## Constraints

- Keep the `probe` Deployment and the `shuttle` and `drifter` pods running and unchanged.
- Give `blocked-server` a label of its own, so no allow rule for `shuttle` matches it.
- Do not open any other egress path for `shuttle`.

## How the answer is checked

The grader runs three checks. The first reads the NetworkPolicy `shuttle-egress` and needs the pod selector `app: shuttle`, the policy type `Egress` only, a DNS rule to `k8s-app: kube-dns` in `kube-system` on UDP and TCP port 53, and a rule to `app: probe` on TCP port 8080. The second reads the pod `blocked-server` and needs the label, container, image and command above, with the pod running and ready. The third runs `nslookup` from `shuttle` and needs an `Address` line, asks `http://probe/` from `shuttle` and needs `version=v1`, then proves that `blocked-server` answers `drifter` on port 8080 and that the same request from `shuttle` times out after 3 seconds. Every check also needs the `probe` Deployment fully rolled out.

Hint: Calico updates its rules a few seconds after you apply a policy. Repeat your test requests before you submit.
