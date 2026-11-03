---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Save The Failing API Server Check Ids

Run kube-bench for the control plane and record which API server checks fail.

## Starting state

The kind cluster has two healthy `probe` replicas in the `starfleet` namespace, a `shuttle` client pod, and one control plane node that runs with the kubeadm defaults. The `kube-bench` image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on both nodes. No kube-bench result has been collected.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-02-01" || exit 1
```

## Required result

The security team of the `starfleet` cluster needs the list of failing API server checks before it plans fixes.

- Run `kube-bench` with the `master` target on the control plane node, as a Job in the `default` namespace.
- Find every check with the state `FAIL` whose number starts with `1.2.`.
- Save the numbers in a file named `failing-1-2.txt`, one number on each line.
- Create the ConfigMap `failing-checks` in the `starfleet` namespace with the content of that file under the key `ids`.

Do not change any setting of the cluster. The grader runs `kube-bench` again and compares its failing `1.2.` checks with your list. If you fix a setting, your list no longer matches.

## Verify The Result

The grader reads the ConfigMap and compares it with a fresh run of the audit. A list that is too short, too long, or that holds a number outside `1.2.` fails. Wait until your Job has completed before you build the list, so that the log is complete.
