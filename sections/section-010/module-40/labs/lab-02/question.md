# Allow Only DNS Egress Under A Baseline

In namespace `starfleet-031-010-04-02`, the NetworkPolicy `default-deny-all` isolates the pods `navigator` and `cargo` (labels `app: navigator` and `app: cargo`) for both directions. The `navigator` pod must resolve names again and reach nothing else.

1. Create a NetworkPolicy named `navigator-dns` in `starfleet-031-010-04-02` that selects only the pod labelled `app: navigator` and allows egress only on UDP port 53 and TCP port 53 to the CoreDNS pods (`k8s-app: kube-dns` in `kube-system`). Select the namespace by its name label and the pods by `k8s-app: kube-dns` in one peer entry.
2. The `navigator` pod resolves `kubernetes.default.svc.cluster.local`.
3. The `navigator` pod times out to the CoreDNS metrics port 9153 and to pod `cargo` on TCP port 8080, and `cargo` still cannot resolve names.

Do not change `default-deny-all`, do not change `cargo` and do not create any other NetworkPolicy.
