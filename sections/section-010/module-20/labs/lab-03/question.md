# Deny All Egress And Observe DNS Fail

The pods in the namespace `dock-031-010-02-03` (pods `hauler` and `winch`, TCP port 8080) must not open any outgoing connection until the team has listed what they need. Other pods must still be able to call them.

Create a NetworkPolicy named `default-deny-egress` in `dock-031-010-02-03` that:

1. selects every pod in the namespace for egress and allows no egress, so `hauler` times out to `winch` and to pod `pilot` (namespace `outpost-031-010-02-03`);
2. also blocks DNS, so `winch` can no longer resolve names through CoreDNS;
3. names only `Egress` in `policyTypes`, so `pilot` still reaches `hauler` and `winch`.

Do not create any other NetworkPolicy in either namespace.
