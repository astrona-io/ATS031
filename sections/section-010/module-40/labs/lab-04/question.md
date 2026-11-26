# Record A Test Matrix For A Policy Set

The NetworkPolicies `default-deny-all`, `hangar-ingress` and `rover-egress` in `starfleet-031-010-04-04` control the pods `rover`, `tanker`, `hangar` and `vault`, and pod `drone` runs in `outpost-031-010-04-04`. Record what the policy set allows today in a ConfigMap named `test-matrix` in `starfleet-031-010-04-04`, one key per row below. Send traffic rows to the pod IP address of the target on TCP port 8080, and record `open` or `blocked`. For DNS rows, look up `kubernetes.default.svc.cluster.local` and record `resolved` or `unresolved`.

1. Rows from pods in `starfleet-031-010-04-04`: `rover-to-hangar`, `rover-to-vault`, `tanker-to-hangar` (key `<source>-to-<target>`).
2. Rows from `drone` in `outpost-031-010-04-04`: `drone-to-hangar`, `drone-to-vault`.
3. DNS rows from `rover` and `tanker`: `rover-dns`, `tanker-dns`.

Do not change, add or delete any NetworkPolicy in either namespace.
