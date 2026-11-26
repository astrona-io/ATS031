# Close Metadata Gaps Across Namespaces

The metadata server at `http://169.254.169.254/latest/meta-data/` must be blocked in `starfleet-031-040-02-04`, `outpost-031-040-02-04` and `dock-031-040-02-04`, for the pods that run now and for pods that start later. Some NetworkPolicies already exist, but not every namespace is covered. Pods with the label `role: cloud-agent` in `starfleet-031-040-02-04`, today pod `agent`, need the address on TCP port 80.

1. In `outpost-031-040-02-04`, `drifter` and any new pod are blocked from `169.254.169.254` and still reach `http://probe/`.
2. In `dock-031-040-02-04`, `tender` and any new pod are blocked from `169.254.169.254` and still reach `http://probe/`.
3. In `starfleet-031-040-02-04`, `agent` and new pods with `role: cloud-agent` reach `169.254.169.254`, while `shuttle` and new pods without the label stay blocked; all of them still reach `http://probe/`.

Do not add or remove labels, do not delete pods, and change nothing in `metadata-stub-031-040-02-04`.
