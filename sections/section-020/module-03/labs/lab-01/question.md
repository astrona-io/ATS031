---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Enable Audit Logging On The API Server

Allow about 15 minutes for the tasks.

After an incident on the `starfleet` cluster nobody could tell who deleted a ConfigMap. The security team has written an audit policy. Turn it on.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-03-01` is the control plane and also runs the pods. The `starfleet-031-020-03-01` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. An audit policy is staged in `/opt/training/audit-policy.yaml` on the control plane node. No component uses it yet, and the API server writes no audit log.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-03-01
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-03-01`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- Copy the staged policy to `/etc/kubernetes/policy/audit-policy.yaml` on the control plane node, without changes.
- The API server runs with `--audit-policy-file=/etc/kubernetes/policy/audit-policy.yaml` and `--audit-log-path=/var/log/kubernetes/audit/audit.log`. Mount both host directories into the API server pod at the same paths.
- The API server runs with `--audit-log-maxage`, `--audit-log-maxbackup` and `--audit-log-maxsize`, each set to a number above zero.
- The API server is ready, writes audit events to the log file, and both `probe` replicas stay available.

Keep every backup outside `/etc/kubernetes/manifests`.

## Verify The Result

The grader reads the command line of the running `kube-apiserver` process, compares the policy file on the node with the staged policy, creates a test ConfigMap and looks for it in the audit log.
