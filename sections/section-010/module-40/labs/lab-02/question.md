---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow Only DNS Egress Under A Baseline

Allow about 8 minutes for the tasks.

The `navigator` must look up names again. It needs nothing else for now, and the `cargo` pod stays fully closed.

## Connect to the lab

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-04-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-04-02" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

## Starting state

The namespace `starfleet-031-010-04-02` runs the pods `navigator` and `cargo`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. The NetworkPolicy `default-deny-all` isolates every pod in the namespace for ingress and egress, so no pod can resolve names. CoreDNS, the cluster DNS server, runs in `kube-system` in pods with the label `k8s-app: kube-dns`.

## Tasks

1. In `starfleet-031-010-04-02`, create a NetworkPolicy named `navigator-dns` that selects only the pod with the label `app: navigator`.
2. Allow egress from `navigator` to the CoreDNS pods in `kube-system` on UDP port 53 and TCP port 53. Select the namespace by its name label and the pods by `k8s-app: kube-dns` in one peer entry.
3. Allow no other egress, keep `default-deny-all` unchanged, and do not change `cargo`.

## Check your work

The test client prints `resolved` with the address, or `unresolved` when the lookup gets no answer:

```sh
kubectl -n starfleet-031-010-04-02 exec navigator -- python /app/client.py dns kubernetes.default.svc.cluster.local
kubectl -n starfleet-031-010-04-02 exec cargo -- python /app/client.py dns kubernetes.default.svc.cluster.local
```

The first command must print `resolved` and the second `unresolved`.
