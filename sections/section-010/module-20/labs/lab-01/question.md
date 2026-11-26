# Apply A Default-Deny Baseline And Allow One Path

The namespace `outpost-031-010-02-01` must start from "nothing is allowed". After that, only pod `smith` may send requests to pod `forge` (label `app: forge`, TCP port 8080).

In `outpost-031-010-02-01`:

1. create a NetworkPolicy named `default-deny-all` that selects every pod for both ingress and egress and has no rules, so pod `idler` can neither send, receive nor resolve names;
2. add a policy that lets `forge` accept TCP port 8080 only from pods labelled `app: smith`, so pod `visitor` (namespace `dock-031-010-02-01`) still times out to `forge`;
3. add a policy that lets `smith` send only to pods labelled `app: forge` on TCP port 8080.

Do not open anything else: no rule may reach every pod, every namespace or a wide address range, and no policy may give `idler` any traffic.
