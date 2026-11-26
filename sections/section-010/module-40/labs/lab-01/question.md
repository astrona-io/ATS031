# Repair A Broken Policy Set

In namespace `starfleet-031-010-04-01`, the `pathfinder` pod (label `app: pathfinder`) cannot resolve names and cannot reach the `datastore` pod (label `app: datastore`, TCP port 6379). Two NetworkPolicies are broken: `pathfinder-egress` and `datastore-ingress`.

Repair them so that:

1. `pathfinder-egress` allows UDP port 53 and TCP port 53 to the CoreDNS pods (`k8s-app: kube-dns` in `kube-system`), and `pathfinder` resolves names;
2. `pathfinder` reaches the `datastore` on TCP port 6379 and the API server through the `kubernetes` Service on port 443, while it still times out to pod `stranger`; keep the `datastore` rule and the `/32` API server rule of `pathfinder-egress`;
3. `datastore-ingress` isolates the `datastore` pod for ingress and admits TCP port 6379 only from `pathfinder`, so `stranger` times out to the `datastore`.

Do not change `default-deny-all` and do not add rules that open every pod, every namespace or every port.
