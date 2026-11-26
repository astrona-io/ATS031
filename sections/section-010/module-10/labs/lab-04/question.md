# Find The Policy That Blocks A Request

In namespace `outpost-031-010-01-04`, pod `lander` must reach pod `depot` on TCP port 8080, but every request times out. The NetworkPolicies `default-deny-all`, `lander-egress` and `depot-ingress` were written for exactly this path.

Find the policy that blocks the request and repair it in place so that:

1. `lander` reaches `depot` on TCP port 8080;
2. `default-deny-all` stays unchanged, only the three policies exist, and the repaired rule admits only pods labelled `app: lander` on TCP port 8080;
3. pod `stray` still times out to `depot`, and `lander` still times out to `stray`.

Keep the policy names. Do not delete `default-deny-all` or add allow rules to it.
