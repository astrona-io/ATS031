# Isolate One Pod For Egress Only

In namespace `starfleet-031-010-01-03`, pod `relay` (label `app: relay`) must stop opening connections of its own, while pods `courier` and `lander` can still send requests to it on TCP port 8080.

Create a NetworkPolicy named `relay-egress-isolation` in `starfleet-031-010-01-03` that:

1. selects only pod `relay`, lists only `Egress` in `policyTypes` and has no egress rules;
2. makes `relay` time out to pod `lander` on TCP port 8080 and fail its DNS lookups;
3. leaves ingress to `relay` open, so `courier` still reaches `relay` on TCP port 8080 and `lander` and `courier` keep their own traffic and DNS.

Do not change pods `lander` and `courier`, and do not create any other NetworkPolicy in the namespace.
