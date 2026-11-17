---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Read A kube-bench Check Definition

Allow about 8 minutes for the tasks.

A reviewer of the `starfleet` cluster wants to know what kube-bench really tests for API server profiling in one benchmark edition. Read it from the definition files, not from a report.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-02-02` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The `kube-bench` image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on both nodes. The ConfigMap `audit-request` in the `starfleet-031-020-02-02` namespace names one benchmark edition under the key `edition`.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-02-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-02-02" || exit 1
node_name="astro-ats-031-lab-020-02-02-control-plane"
worker_name="astro-ats-031-lab-020-02-02-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

Create the ConfigMap `check-definition` in the `starfleet-031-020-02-02` namespace with two keys:

- `files`: the names of the files in the directory of the requested edition inside the image (`/opt/kube-bench/cfg/<edition>`), one name on each line.
- `apiserver-profiling-check`: the `id` of the check in the `master.yaml` file of that edition whose `text` asks for the API server `--profiling` argument. Its `id` starts with `1.2.`.

Do not run an audit and do not change the cluster.

## Verify The Result

The grader starts its own short pod with the same image, lists the directory of the requested edition and reads its `master.yaml` file. The order of the file names does not matter.
