---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Enable Audit Logging On The API Server

Allow about 15 minutes for the tasks.

After an incident on the `starfleet` cluster nobody could tell who deleted a ConfigMap. The security team has written an audit policy. Turn it on.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-03-01` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. An audit policy is staged in `/opt/training/audit-policy.yaml` on the control plane node. No component uses it yet, and the API server writes no audit log.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-03-01" || exit 1
node_name="astro-ats-031-lab-020-03-01-control-plane"
worker_name="astro-ats-031-lab-020-03-01-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

- Copy the staged policy to `/etc/kubernetes/policy/audit-policy.yaml` on the control plane node, without changes.
- The API server runs with `--audit-policy-file=/etc/kubernetes/policy/audit-policy.yaml` and `--audit-log-path=/var/log/kubernetes/audit/audit.log`. Mount both host directories into the API server pod at the same paths.
- The API server runs with `--audit-log-maxage`, `--audit-log-maxbackup` and `--audit-log-maxsize`, each set to a number above zero.
- The API server is ready, writes audit events to the log file, and both `probe` replicas stay available.

Keep every backup outside `/etc/kubernetes/manifests`.

## Verify The Result

The grader reads the command line of the running `kube-apiserver` process, compares the policy file on the node with the staged policy, creates a test ConfigMap and looks for it in the audit log.
