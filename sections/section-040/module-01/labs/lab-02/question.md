---
exam_objectives:
- Protect node metadata and endpoints
---
# Restrict A Pod To An Egress Allow-List

Allow about 8 minutes for the tasks.

Limit the outgoing traffic of one workload to the destinations it needs, so that a metadata-style endpoint is blocked.

## Starting state

The namespace `starfleet-031-040-01-02` has the `probe` Deployment with two replicas and the `probe` Service on port 80, which forwards to port 8080 of the pods. It also has the client pod `courier` with the label `app=courier` and the pod `metadata-simulator`, a web server on port 8080 that stands in for a metadata endpoint. The namespace `outpost-031-040-01-02` has the web server pod `beacon` on port 8080 and the client pod `drifter`. No NetworkPolicy exists.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-01-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-01-02" || exit 1
```

Keep this connection selected for the whole task.

## Required result

The `courier` workload calls the `probe` Service by its name and has no other dependency. Create a NetworkPolicy in `starfleet-031-040-01-02` that applies to pods with the label `app=courier` and allows only the egress they need:

- DNS requests to the cluster DNS pods (the pods with the label `k8s-app=kube-dns` in `kube-system`) on port 53, UDP and TCP;
- requests to the `probe` pods on port 8080.

All other egress from these pods must be blocked, including `metadata-simulator` and `beacon`. Do not change other pods: `drifter` must still reach `metadata-simulator` and `beacon`. Do not delete or relabel pods.

## Verify the result

The grader sends live requests from `courier` and `drifter` to the pod IP addresses of `metadata-simulator` and `beacon` and to the `probe` Service. It also starts a new pod with the label `app=courier`, sends the same requests from it and removes it again. Wait a few seconds after you apply a policy, because the network plugin needs a moment to program it.
