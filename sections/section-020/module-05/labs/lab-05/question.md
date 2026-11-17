---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Restrict The Kubelet Service Files And Turn On Certificate Rotation

Allow about 10 minutes for the tasks.

The worker node review of the `starfleet` cluster lists two findings: readable kubelet service files and a kubelet that no longer renews its client certificate. Fix both.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-05-05` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The systemd unit files of the kubelet on the worker node have mode `644`, and certificate rotation is turned off. A copy of the original kubelet configuration is in `/opt/training/backup/kubelet-config.yaml` on the worker node.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-05-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-05-05" || exit 1
node_name="astro-ats-031-lab-020-05-05-control-plane"
worker_name="astro-ats-031-lab-020-05-05-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

- The kubelet unit file and every drop-in file of the `kubelet` service on the worker node `astro-ats-031-lab-020-05-05-worker` have mode `600` or stricter and the owner `root:root`. Find the files with `systemctl`.
- The effective configuration of the kubelet has `rotateCertificates` set to `true`.
- The worker node is `Ready`, and both `probe` replicas stay available.

## Verify The Result

The grader asks systemd on the worker node for the unit file and the drop-in files of the `kubelet` service, reads their modes with `stat`, and reads the effective kubelet configuration through the `configz` endpoint.
