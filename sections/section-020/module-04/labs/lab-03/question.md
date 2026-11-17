---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Require Client Certificates On etcd

Allow about 12 minutes for the tasks.

A scan of the `starfleet` control plane reports that etcd answers requests that bring no certificate. Close the gap.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-04-03` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. etcd runs as a static pod on the control plane node. Someone turned off client certificate authentication for the client and the peer ports of etcd. A copy of the etcd manifest from before that change is in `/opt/training/backup/etcd.yaml` on the control plane node.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-04-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-04-03" || exit 1
node_name="astro-ats-031-lab-020-04-03-control-plane"
worker_name="astro-ats-031-lab-020-04-03-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

- etcd runs with `--client-cert-auth=true` and `--peer-client-cert-auth=true`.
- A request to `https://127.0.0.1:2379/health` on the control plane node without a client certificate fails.
- The API server stays ready, and both `probe` replicas stay available.

Keep every backup outside `/etc/kubernetes/manifests`.

## Verify The Result

The grader reads the command line of the running `etcd` process and sends a request without a client certificate to the client port of etcd from the control plane node.
