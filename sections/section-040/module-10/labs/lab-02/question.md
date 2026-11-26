# Restrict A Pod To An Egress Allow-List

Pod `courier` (label `app: courier`) in `starfleet-031-040-01-02` needs only DNS and the `probe` Service at `http://probe/`. Today it can also reach pod `metadata-simulator` in the same namespace and pod `beacon` in `outpost-031-040-01-02`, both on TCP port 8080.

1. Add an egress NetworkPolicy so that `courier` can no longer reach `metadata-simulator`.
2. `courier`, and any new pod labelled `app: courier`, still reach `http://probe/`.
3. Pods labelled `app: courier` reach nothing outside DNS and `probe`, while pods with other labels in the namespace keep their egress.

Keep the label of `courier`, and keep `metadata-simulator` and `beacon` reachable from pod `drifter` in `outpost-031-040-01-02`.
