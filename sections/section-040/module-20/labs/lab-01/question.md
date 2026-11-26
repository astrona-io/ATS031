# Block The Metadata Address For A Namespace

A metadata server answers at `http://169.254.169.254/latest/meta-data/`, and every pod in the cluster can reach it. The pods of `outpost-031-040-02-01`, today pod `drifter` and any pod that starts there later, must lose that path and keep every other one.

1. Add an egress NetworkPolicy in `outpost-031-040-02-01` so that `drifter` can no longer reach `169.254.169.254`.
2. `drifter` still reaches `http://probe/` in its namespace and `http://probe.starfleet-031-040-02-01.svc.cluster.local/` by DNS name.
3. A new pod in `outpost-031-040-02-01`, whatever its labels, is blocked from `169.254.169.254` and still reaches both Services.

Change nothing in `starfleet-031-040-02-01`, `dock-031-040-02-01` or `metadata-stub-031-040-02-01`: their pods must still reach the metadata server.
