# Allow API Server Egress For One Pod

In namespace `starfleet-031-010-04-03`, the NetworkPolicies `default-deny-all` and `allow-dns` let the pods `operator` and `helper` (labels `app: operator` and `app: helper`) reach only CoreDNS. The `operator` pod must talk to the Kubernetes API server again; `helper` must not.

Create a NetworkPolicy named `operator-to-api-server` in `starfleet-031-010-04-03` that selects only the pod labelled `app: operator`, so that:

1. its egress rule allows the address and TCP port that the `kubernetes` Service in namespace `default` sends requests to (its endpoint), not the Service address and port 443;
2. `operator` reaches the API server through the `kubernetes` Service on port 443;
3. the rule is one `ipBlock` with a `/32` range on that one TCP port: `helper` times out to the API server and still resolves names, and `operator` times out to `helper` on TCP port 8080.

Do not change `default-deny-all` or `allow-dns`.
