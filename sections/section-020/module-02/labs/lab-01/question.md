---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Save The Failing API Server Check Ids

Solve this question on: `terminal`

The security team needs the list of failing API server checks before it plans fixes. The kind cluster has two healthy `probe` replicas in the namespace `starfleet-031-020-02-01`, a `shuttle` client pod, and one control plane node that runs with the kubeadm defaults. kube-bench is a tool that runs the Center for Internet Security (CIS) Kubernetes benchmark checks on a node. Its image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on both nodes. No kube-bench result has been collected.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-02-01" || exit 1
```

Allow about 10 minutes for task work. Cluster startup adds time.

## Tasks

1. Run `kube-bench` with the `master` target on the control plane node, as a Job in the `default` namespace. Wait until the Job has completed, so that its log is complete.
2. From the log, find every check with the state `FAIL` whose number starts with `1.2.`. Save the numbers in a file named `failing-1-2.txt`, one number on each line.
3. Create the ConfigMap `failing-checks` in the namespace `starfleet-031-020-02-01` with the content of that file under the key `ids`.

## Constraints

- Do not change any setting of the cluster. The grader runs `kube-bench` again and compares its failing `1.2.` checks with your list. If you fix a setting, your list no longer matches.
- Put only `1.2.` check numbers in the list.

## How the answer is checked

The grader runs two checks. The first reads the ConfigMap `failing-checks` in `starfleet-031-020-02-01` and needs a key `ids` that is not empty and that holds only numbers of the form `1.2.<n>`, one on each line. The second starts its own `kube-bench` Job in the `default` namespace, waits for it to complete, and needs your list to be exactly the set of `1.2.` checks that fail in that run. A list that is too short or too long fails. Both checks also need `/readyz` of the API server to return `ok`.

Hint: the `--json` option of `kube-bench` makes the failing checks easy to filter.
