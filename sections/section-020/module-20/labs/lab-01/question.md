# Save The Failing API Server Check Ids

The security team needs the list of failing API server checks in a form that a script can read, before it plans fixes. The `kube-bench` image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on the node, and the control plane runs with the kubeadm defaults.

1. Create the Job `api-server-audit` in namespace `starfleet-031-020-02-01` that runs `kube-bench run --targets master --json` on the control plane node.
2. Let the Job complete, so its log holds the kube-bench JSON report.
3. From that report, take every check with the status `FAIL` whose number starts with `1.2.`, and create the ConfigMap `failing-checks` in the same namespace with these numbers under the key `ids`, one number on each line.

Do not change any setting of the cluster; the grader runs kube-bench again and compares its failing `1.2.` checks with your list.
