---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Summary

`kube-bench` runs the audit commands of a benchmark edition on one node and prints a result for each recommendation. The rules are definition files, not program code. Each check has an identifier, an audit command, a test that compares the output with an expected value, and a remediation text. Because the audits read the processes and files of the node, the tool must run where they are. In a cluster that means a Job with the host process namespace, host directory mounts, and a node selector and toleration for the control plane.

The target selects the group of checks: `master`, `etcd`, `controlplane`, `node` and `policies`. The benchmark edition selects the version of the rules. The tool chooses an edition from the Kubernetes version it detects, and `--benchmark` and `--version` override that choice. A cluster that is newer than the newest edition can be judged by an older edition, so a report must name the edition that was used.

A result is `PASS`, `FAIL`, `WARN` or `INFO`. Read the summary counts first, then the failures, then the remediation for the failures that matter, and search by the setting name because check numbers change. Use `--check` and `--group` to rerun part of a target, and `--json` with `jq` to export results. Save a baseline before a fix and compare the failing lists after it.

Automated results have limits. A `WARN` is a manual task. A `PASS` covers only what the audit looked at. A kind node can produce findings that do not apply to a production cluster, and an old edition can fail a check for a flag that no longer exists. A good review lists the fixes with evidence, the exceptions with reasons, and the manual decisions, and treats the counts as an attachment.

Key facts to remember:

- Checks come from definition files for one benchmark edition.
- The audit reads node processes and files, so the tool needs `hostPID` and host mounts in a Job.
- `--targets`, `--benchmark`, `--version`, `--check`, `--group` and `--json` control what runs and what is printed.
- Name the edition in every report, and never change a cluster only to clear a mismatched check.

<!-- astrona:playground:destroy -->
