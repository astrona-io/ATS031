---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Enable NodeRestriction

Allow about 10 minutes for the tasks.

The security team of the `starfleet` cluster asks what an attacker could do with the kubelet credentials of one node. Today the answer is: put any label on its own node, even the labels that should steer sensitive pods. Limit what a kubelet may write.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-03-05` is the control plane and also runs the pods. The `starfleet-031-020-03-05` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The API server runs without the `NodeRestriction` admission plugin.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-03-05
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-03-05`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- The API server on the control plane node runs with `NodeRestriction` in `--enable-admission-plugins`, and the plugin is not in `--disable-admission-plugins`.
- The kubelet credentials of the node (`/etc/kubernetes/kubelet.conf` on the node) can no longer add a label with the prefix `node-restriction.kubernetes.io/` to the node.
- Keep the other admission plugins that the API server uses now.
- The API server stays ready and both `probe` replicas stay available.

## Verify The Result

The grader reads the command line of the running `kube-apiserver` process. It then runs `kubectl` on the node with the kubelet kubeconfig and tries to add the label `node-restriction.kubernetes.io/lab-check=kubelet` to the node. It removes the label again if the request succeeds.
