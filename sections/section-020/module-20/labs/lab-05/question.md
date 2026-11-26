# Record The Totals Of A kube-bench Report

The platform team tracks its benchmark progress in numbers. Run the control plane audit and record the numbers of this run. The image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on the node.

1. Create the Job `master-audit` in namespace `starfleet-031-020-02-05` that runs `kube-bench run --targets master` on the control plane node, and let it complete.
2. Create the ConfigMap `master-result` in the same namespace with the keys `pass`, `fail`, `warn` and `info`: the totals in the summary at the end of the log of `master-audit`.
3. In the same ConfigMap, add the key `fail-1.1` with the number of `[FAIL]` lines for checks in section `1.1` (control plane node configuration files), and the key `fail-1.2` with the number for section `1.2` (API server).

Do not change the cluster after the run; the grader compares your numbers with the log of your finished `master-audit` pod.
