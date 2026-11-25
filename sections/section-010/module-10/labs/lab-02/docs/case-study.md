---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

The namespace `starfleet-031-010-01-02` runs the Deployment `archive` with two replicas and the Service `archive`, plus the pods `scanner`, `decoy` and `idler`. The Service listens on port 80 and sends requests to the container port named `http`, which is TCP port 8080. The `decoy` pod is a healthy listener on TCP port 8080 with the label `app: decoy`; it is there to prove that unlisted egress is blocked. Each pod has the label `app: <name>` and contains a small test client, `/app/client.py`. No NetworkPolicy exists. CoreDNS, the cluster DNS server, runs in `kube-system` in pods with the label `k8s-app: kube-dns`.
