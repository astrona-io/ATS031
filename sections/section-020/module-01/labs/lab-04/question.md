---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Report The Effective Kubelet Settings

Allow about 10 minutes for the tasks.

A colleague reviewed only the kubelet configuration file of the `starfleet` node and reported that everything is closed. Check what the kubelet really runs with.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-01-04` is the control plane and also runs the pods. The `starfleet-031-020-01-04` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The kubelet on the node runs with a setting that is not in its configuration file. The file `/var/lib/kubelet/config.yaml` on the node has mode `644`.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-01-04
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-01-04`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- Create the ConfigMap `kubelet-review` in the `starfleet-031-020-01-04` namespace with three keys that hold the **effective** values of the kubelet on the node:
  - `anonymous-enabled`: `true` or `false`, from `authentication.anonymous.enabled`.
  - `authorization-mode`: the value of `authorization.mode`, for example `Webhook`.
  - `read-only-port`: the number in `readOnlyPort`, for example `0`.
- Set the mode of `/var/lib/kubelet/config.yaml` on the node to `600` or stricter, with the owner `root:root`.
- Do not change any other kubelet setting. The node stays `Ready`.

## Verify The Result

The grader reads the effective kubelet configuration of the node through the API server (`configz`) and compares it with your ConfigMap. It also runs `stat` on the configuration file.
