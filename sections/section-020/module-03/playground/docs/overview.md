---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Guided Practice: Harden The API Server In A Private Playground

This ungraded playground has one control plane node and one worker node. The API server runs with weak settings on purpose. Use a host shell with the private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

<!-- astrona:playground:renew -->

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-playground-020-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-playground-020-03" || exit 1
NODE=astro-ats-031-playground-020-03-control-plane
```

Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Starting state

The `starfleet` namespace has the `probe` Deployment, the `probe` Service and the `shuttle` pod. On the control plane node, `/opt/training/audit-policy.yaml` holds an audit policy that nothing uses, `/opt/training/backup` holds a copy of every original manifest, and three manifests have mode `644`.

```sh
kubectl -n starfleet get pods -o wide
podman exec $NODE ls -l /etc/kubernetes/manifests /opt/training/backup
```

## Suggested exercises

1. Break the scheduler manifest with an unknown flag, read the reason with `crictl logs`, and restore the backup.
2. Read the authentication and authorization flags of the API server and test anonymous access with `kubectl auth can-i`.
3. Enable audit logging with the staged policy, the log flags and the two host path mounts.
4. Add `--profiling=false` to the API server, the controller manager and the scheduler.
5. Set mode `600` and owner `root:root` on the three widened manifests.

Always edit a copy outside `/etc/kubernetes/manifests`, move it in, and read the running pod arguments afterwards.

## Common pitfalls

> [!WARNING]
> Keep backups outside the manifests directory. A restart of the API server takes tens of seconds, and `kubectl` does not answer during that time. This guide does not record a completed run.
