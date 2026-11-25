---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Guided Practice: Review The Kubelet And CoreDNS

This ungraded playground is one virtual machine (VM) that runs a single-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node is the control plane and also runs your pods. The kubelet, the agent that starts the containers of the pods on a node, runs with weak settings on purpose: anonymous requests are enabled, the authorization mode is `AlwaysAllow`, the read-only port `10255` is open, and two kubelet files have mode `644`.

kube-bench, the tool that checks a node against the Center for Internet Security (CIS) Kubernetes Benchmark, is installed in `/usr/local/bin/kube-bench`, with its benchmark files in `/etc/kube-bench/cfg`.

<!-- astrona:playground:renew -->

Open a shell on the node. You log in as the `student` user, which has `sudo` and a kubeconfig file for the cluster. A kubeconfig file tells kubectl, the Kubernetes command-line tool, which cluster to use and which credentials to send.

```sh
astrona ssh astro-ats-031-playground-020-05
kubectl config current-context
NODE=astro-ats-031-playground-020-05
```

The second command prints `kubernetes-admin@astro-ats-031-playground-020-05`. Commands that use `sudo` change only this VM. They do not touch your own computer.

## Inspect

Read the effective kubelet settings through the API server, and the file modes on the node:

```sh
kubectl get --raw "/api/v1/nodes/$NODE/proxy/configz" | python3 -m json.tool | grep -A1 -e '"anonymous"' -e '"mode"' -e readOnlyPort
sudo stat -c '%a %n' /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
```

The output shows `"readOnlyPort": 10255`, `"enabled": true` under `"anonymous"` and `"mode": "AlwaysAllow"`, and mode `644` for both files.

Then read the CoreDNS Deployment and its Corefile:

```sh
kubectl -n kube-system get deployment coredns
kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}'
```

The `coredns` Deployment shows `2/2` ready replicas.

A copy of the original kubelet configuration is in `/opt/training/backup/kubelet-config.yaml` on the node. The kubelet stops if its configuration file has a duplicate key, so always remove a key before you append it again. After each change, run `sudo systemctl restart kubelet` and check that `kubectl get nodes` still shows the node `Ready`.

## Common pitfalls

> [!WARNING]
> Set the four kernel parameters that `protectKernelDefaults` checks (`vm.overcommit_memory`, `vm.panic_on_oom`, `kernel.panic`, `kernel.panic_on_oops`) in a file in `/etc/sysctl.d` before you turn the field on. Without the file, the values are lost at the next reboot and the kubelet refuses to start. This node runs the control plane, so a kubelet that does not start also stops the restart of the API server if it fails; keep a backup of every file you edit.
