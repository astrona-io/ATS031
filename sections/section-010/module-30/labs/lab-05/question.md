# Allow A TCP Port Range And A Named UDP Port

In namespace `starfleet-031-010-03-05`, pod `meter` (label `app: meter`) listens on TCP ports 7000, 7001, 7002 and 7100, and on UDP port 7200, which its pod spec names `tick`. Only pod `surveyor` in namespace `outpost-031-010-03-05` may reach it; pod `loiterer` in the same namespace may not.

Create a NetworkPolicy named `meter-ports` in `starfleet-031-010-03-05` that selects the `meter` pod for ingress, admits senders through one peer entry with a `namespaceSelector` for `outpost-031-010-03-05` and a `podSelector` for `app: surveyor`, and:

1. allows TCP ports 7000 to 7002 with a single port item that uses `endPort`, so `surveyor` reaches all three and `loiterer` is blocked;
2. allows UDP by the container port name `tick`, not by its number, so `surveyor` gets a UDP reply on port 7200;
3. keeps TCP port 7100 closed for `surveyor` and gives `loiterer` no UDP reply on port 7200.

Use exactly these two port items and create no other NetworkPolicy.
