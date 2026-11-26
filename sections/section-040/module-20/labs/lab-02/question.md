# Allow The Metadata Address For One Labelled Pod

In `starfleet-031-040-02-02`, pod `agent` (labels `app: agent`, `role: cloud-agent`) needs the metadata server at `http://169.254.169.254/latest/meta-data/`. Pod `shuttle` (label `app: shuttle`) and every other pod in the namespace must lose it. The label `role: cloud-agent` decides, not the pod name.

1. Add egress NetworkPolicies so that `shuttle` can no longer reach `169.254.169.254` and still reaches `http://probe/`.
2. `agent` still reaches `169.254.169.254` on TCP port 80 and `http://probe/`.
3. A new pod without labels is blocked from `169.254.169.254`, a new pod with `role: cloud-agent` reaches it, and both reach `http://probe/`.

Do not change the labels of `agent` or `shuttle`, and change nothing in `outpost-031-040-02-02`, `dock-031-040-02-02` or `metadata-stub-031-040-02-02`.
