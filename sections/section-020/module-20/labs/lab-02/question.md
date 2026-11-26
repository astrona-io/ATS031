# Read A kube-bench Check Definition

A reviewer wants to know what kube-bench really tests for API server profiling in one benchmark edition. The ConfigMap `audit-request` in namespace `starfleet-031-020-02-02` names that edition under the key `edition`, and the image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on the node. Read the answer from the definition files in the image, not from a report, and record it in the ConfigMap `check-definition` in the same namespace.

1. Under the key `files`, list the names of the files in `/opt/kube-bench/cfg/<edition>` inside the image, one name on each line.
2. Under the key `apiserver-profiling-check`, record the `id` of an API server check: one from section `1.2` of the `master.yaml` file of that edition.
3. Make that `id` the check whose `text` asks for the API server `--profiling` argument.

Do not run an audit (`kube-bench run`) and do not change the cluster.
