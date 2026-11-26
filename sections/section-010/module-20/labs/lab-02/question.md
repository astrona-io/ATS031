# Deny All Ingress In One Namespace

Nothing may open a connection to a pod in the namespace `dock-031-010-02-02` (pods `vault` and `crane`, TCP port 8080) until the team writes allow rules. The pods in `dock-031-010-02-02` must still be able to call out.

Create a NetworkPolicy named `default-deny-ingress` in `dock-031-010-02-02` that:

1. selects every pod in the namespace for ingress and allows no ingress, so pod `visitor` (namespace `outpost-031-010-02-02`) times out to `vault` and `crane`;
2. also blocks traffic inside the namespace, so `vault` and `crane` time out to each other;
3. names only `Ingress` in `policyTypes`, so `crane` still reaches `visitor` and `vault` still resolves names through CoreDNS.

Do not create any other NetworkPolicy in either namespace.
