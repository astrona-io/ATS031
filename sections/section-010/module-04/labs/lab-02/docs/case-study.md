---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

The namespace `starfleet-031-010-04-02` runs the pods `navigator` and `cargo`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. The NetworkPolicy `default-deny-all` isolates every pod in the namespace for ingress and egress, so no pod can resolve names. CoreDNS, the cluster DNS server, runs in `kube-system` in pods with the label `k8s-app: kube-dns`.
