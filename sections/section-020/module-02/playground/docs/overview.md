---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Guided Practice: Run kube-bench In A Private Playground

This ungraded playground has one control plane node and one worker node, with the `kube-bench` image loaded on both. Use a host shell with the private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

<!-- astrona:playground:renew -->

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-playground-020-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-playground-020-02" || exit 1
node_name="astro-ats-031-playground-020-02-control-plane"
worker_name="astro-ats-031-playground-020-02-worker"
```

Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Starting state

The `starfleet` namespace has the `probe` Deployment, the `probe` Service and the `shuttle` pod. The cluster uses the kubeadm defaults, so some benchmark checks fail. No `kube-bench` Job exists yet.

```sh
kubectl -n starfleet get pods -o wide
kubectl get nodes -o wide
```

## Suggested exercises

1. Write a Job for the `master` target with `hostPID`, the host mounts, a node selector and a toleration for the control plane taint. Run it and read the summary.
2. Run a Job for the `node` target on the worker and compare its totals with the control plane totals.
3. Run the `etcd` target as its own Job.
4. Export the control plane result with `--json` and list the failing check numbers with `jq`.
5. Run one check with `--check` and note which benchmark edition the first lines of the log name.

Delete finished Jobs with `kubectl -n default delete job <name>` before you reuse a name. The result of a run on a kind node is practice for the workflow. It is not a claim of compliance for any cluster.

## Common pitfalls

> [!WARNING]
> Name the benchmark edition in every note you keep. Do not change a setting only to clear a check that does not fit a kind node.
