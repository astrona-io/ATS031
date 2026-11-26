# Repair Metadata Policies That Do Not Block

Each of `starfleet-031-040-02-03`, `outpost-031-040-02-03` and `dock-031-040-02-03` has a NetworkPolicy named `metadata-guard` that should keep its pods away from the metadata server at `http://169.254.169.254/latest/meta-data/`. None of the three does its job.

1. Repair `metadata-guard` in `starfleet-031-040-02-03`: `shuttle`, `agent` and new pods, with or without `role: cloud-agent`, are blocked from `169.254.169.254` and still reach `http://probe/`.
2. Repair `metadata-guard` in `outpost-031-040-02-03`: `drifter` and new pods are blocked from `169.254.169.254` and still reach `http://probe/`.
3. Repair `metadata-guard` in `dock-031-040-02-03`: `tender` and new pods are blocked from `169.254.169.254` and still reach `http://probe/`.

Change nothing in `metadata-stub-031-040-02-03`: pod `control` must still reach the metadata server.
