---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Manual Checks And False Findings

An automated report ends with counts, and a manager may read only the counts. A reviewer must know what those counts leave out. This part explains what `WARN` and `INFO` mean in practice, why a `PASS` can still hide a risk, why some `FAIL` results are not real findings on a kubeadm node, and how to separate score from risk. It has no commands, because the reasoning applies to the logs you already have.

## Manual checks

Some recommendations cannot be decided by a command. The benchmark marks these as manual. `kube-bench` prints them as `WARN` and shows the audit text for a person to follow. Examples are the questions whether the audit policy covers the right resources, whether the cluster uses a separate certificate authority for etcd, whether secrets are read from files instead of environment variables, and whether network policies exist in every namespace.

A `WARN` is a task, not a pass and not a failure. The reviewer follows the audit text, decides, and records the decision. `INFO` lines carry context, for example a note that a check does not apply to this installation. They are not scored and need no action, but they can explain why a count looks as it does.

## A pass is as good as its audit

Each automated check looks at one thing. A `PASS` for an audit that searches the process arguments means the flag has the right value in the running process. It does not mean that the setting works as intended, that the file in the flag exists, or that the rest of the configuration is safe. An audit policy flag that points to an empty policy file passes the "flag is set" check and records nothing useful.

Two more limits apply. The tool reads the state at the moment of the run, so a later change can undo a fix. And the tool trusts what it reads: a process started with a flag that the audit command does not match, for example through a configuration file instead of a flag, can produce a `FAIL` for a setting that is in fact correct, or a `PASS` for one that is overridden.

## False findings on a kubeadm node

A false finding is a `FAIL` that does not describe a real risk on this cluster. The audit ran, but its expectation does not fit the installation, or something else changed its result. The playground node, a kubeadm node with Kubernetes 1.35 judged by the edition `cis-1.10`, shows two kinds.

The first kind is an expectation that the installation does not share. Check `1.1.12` expects the etcd data directory `/var/lib/etcd` to belong to the user and group `etcd:etcd`. kubeadm runs etcd as a static pod and creates no `etcd` user on the node, so the directory belongs to `root:root` with mode `700`. Only root can read it. The audit is not wrong for an installation that runs etcd as its own user, but on a kubeadm node the right record is "not applicable", not a `chown` to a user that does not exist.

The second kind comes from the way the tool runs. The audits of checks `1.1.7` and `1.1.8` contain the pattern `*etcd*` without quotes, so the shell matches it against the files of the current directory first. On the playground node, running kube-bench from a directory that held a file named `etcd.txt` turned both checks into `FAIL`, and running it from another directory gave `PASS` again. A Job with missing host mounts is similar: it reports `WARN` for checks whose files it cannot see. When the benchmark edition is older than the Kubernetes version, a check can also fail because it looks for a flag or a file that no longer exists.

Not every `FAIL` from the node checks is false. Check `4.1.1` fails because the kubelet systemd unit file `/lib/systemd/system/kubelet.service` has mode `644`, and check `4.1.9` fails because `/var/lib/kubelet/config.yaml` has mode `644`. Those are real settings on a real host, and `chmod 600` fixes both.

Some real findings need a decision before a fix. Check `1.2.5` wants `--kubelet-certificate-authority` on the API server, so that the API server verifies the serving certificate of each kubelet. By default each kubelet of a kubeadm cluster creates its own serving certificate, signed by a certificate authority that only that kubelet knows. Add the flag without first changing how the kubelets get their certificates, and requests from the API server to the kubelet, such as `kubectl logs` and `kubectl exec`, fail. The risk is real, but the fix is a project, so the reviewer records it as an accepted exception with a plan.

For each false finding, the reviewer does not change the cluster to turn the line green. The reviewer reads the audit, finds the real value on the node, and writes down why the finding does not apply. This record is as important as a fix. A reviewer who changes a working cluster to satisfy a mismatched check creates a risk to remove a warning.

```mermaid
flowchart TB
    F["FAIL result"] --> Q{"Is the audit valid here?"}
    Q -->|"no"| X["Record: not applicable and why"]
    Q -->|"yes"| R{"Is the risk real?"}
    R -->|"yes"| Y["Fix and verify"]
    R -->|"no"| Z["Record an accepted exception"]
```

The diagram shows two questions before any change: whether the audit fits this cluster, and whether the risk is real.

## Score versus risk

The summary counts treat all checks equally, and a cluster with fewer failures is not always safer. One failing check on the exposed kubelet port can matter more than ten failing checks on log retention. The benchmark also marks checks as scored or not scored, and profile level 1 or level 2. Level 2 settings can reduce usability and are meant for environments that need stronger protection.

A useful review therefore reports three lists: findings fixed with the evidence, findings accepted or not applicable with the reason, and manual checks decided by a person. The raw counts are an attachment, not the result.

You can now read a `kube-bench` result with its limits in mind. The tool finds candidates. A person decides which findings are real and proves each fix.

## Common pitfalls

> [!WARNING]
> - **Reporting the pass rate as the security level.** The rate says nothing about the risk of the failing checks.
> - **Skipping `WARN` lines.** They are the checks nobody has judged yet.
> - **Changing a working cluster to clear a false finding.** Record the reason instead.
> - **Reporting a managed control plane as checked.** On a managed service you cannot read the control plane, so those results are not yours to claim.
