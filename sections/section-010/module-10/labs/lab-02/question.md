# Allow DNS And One Application Dependency

In namespace `starfleet-031-010-01-02`, pod `scanner` must reach only the `archive` pods (label `app: archive`, TCP port 8080), which it finds by the name of the Service `archive`.

Create a NetworkPolicy named `scanner-egress` in `starfleet-031-010-01-02` that:

1. selects only pod `scanner` for egress and allows only UDP and TCP port 53 to the CoreDNS pods (label `k8s-app: kube-dns` in namespace `kube-system`, both selectors in one peer entry) and TCP port 8080 to the `archive` pods in the same namespace;
2. lets `scanner` resolve the name `archive.starfleet-031-010-01-02.svc.cluster.local` and get a reply from the Service `archive`;
3. makes `scanner` time out to pod `decoy` on TCP port 8080.

Do not change pod `decoy`: pod `idler` must still reach it.
