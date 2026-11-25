# Summary

`kube-bench` runs the audit commands of a benchmark edition on one node and prints a result for each recommendation. The rules are definition files, not program code. Each check has an identifier, an audit command, a test that compares the output with an expected value, and a remediation text.

The audits read the processes and files of the node, so the tool must run where they are. On a node where you have a shell, you run the binary as root with `sudo`. In a cluster, you can run a Job with the host process namespace, host directory mounts, and a node selector and toleration for the control plane. Such a Job sees only the directories it mounts.

The target selects the group of checks: `master`, `etcd`, `controlplane`, `node` and `policies`. The benchmark edition selects the version of the rules. The tool chooses an edition from the Kubernetes version it detects, and `--benchmark` and `--version` override that choice. A cluster that is newer than the newest map entry is judged by an older edition: `kube-bench` v0.10.6 judges Kubernetes 1.35 with `cis-1.10`. The text report does not print the edition, so find it with `--v 1` or in the JSON output, and name it in the report.

A result is `PASS`, `FAIL`, `WARN` or `INFO`. Read the summary counts first, then the failures, then the remediation for the failures that matter. Search by the setting name, because check numbers change between editions. Use `--check` and `--group` to rerun part of a target, and `--json` with `jq` to export results. Save a baseline before a fix and compare the failing lists after it.

Automated results have limits. A `WARN` is a manual task. A `PASS` covers only what the audit looked at. Some failures do not apply to the installation: on a kubeadm node, the etcd data directory belongs to `root`, not to an `etcd` user. Others come from the way the tool runs, such as a Job without a host mount, or a file name that matches an audit pattern. An old edition can also fail a check for a flag that no longer exists.

A good review lists the fixes with evidence, the exceptions with reasons, and the manual decisions. It treats the counts as an attachment.

Key facts to remember:

- Checks come from definition files for one benchmark edition.
- The audit reads node processes and files, so the binary needs `sudo` and a Job needs `hostPID` and host mounts.
- `--targets`, `--benchmark`, `--version`, `--check`, `--group` and `--json` control what runs and what is printed.
- Name the edition in every report, and never change a cluster only to clear a mismatched check.

<!-- astrona:playground:destroy -->
