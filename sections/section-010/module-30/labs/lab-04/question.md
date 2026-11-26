# Allow A Pod Range With ipBlock And except

In namespace `starfleet-031-010-03-04`, pod `ledger` (label `app: ledger`) serves TCP port 7070. The cluster gives pod addresses from `192.168.0.0/16`. Pods `courier` and `rogue` in namespace `outpost-031-010-03-04` send requests to it, and only `courier` may get in.

Create a NetworkPolicy named `ledger-from-pod-range` in `starfleet-031-010-03-04` that:

1. selects the `ledger` pod for ingress and allows TCP port 7070 from an `ipBlock` with the `cidr` `192.168.0.0/16`, so `courier` reaches `ledger`;
2. has one `except` entry that removes exactly the current address of the `rogue` pod as a `/32`;
3. blocks `rogue` from `ledger` on TCP 7070, while `courier` still gets a reply.

Use no peer form other than `ipBlock`, and allow no port other than TCP 7070.
