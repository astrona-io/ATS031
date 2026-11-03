---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Enable Encryption At Rest For Secrets

The security team found that the Secret `launch-code` in `starfleet` is stored in clear text in etcd. Enable encryption at rest for Secrets without stopping the cluster.

## Starting state

The isolated environment has two healthy probe replicas, an internal Service, two client Pods and the Secret `launch-code` in `starfleet`. The API server has no encryption configuration. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

Use a host shell with the private kubeconfig for this independent kind environment.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-04-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-04-01" || exit 1
node_name="astro-ats-031-lab-020-04-01-control-plane"
worker_name="astro-ats-031-lab-020-04-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Required result

1. A file `/etc/kubernetes/enc/encryption-config.yaml` on the control plane node holds an `EncryptionConfiguration` for `secrets` with the `aescbc` provider first and the `identity` provider last. The file has mode `600`.
2. The `kube-apiserver` static pod runs with `--encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml`, and the file is mounted into the pod.
3. The Secret `launch-code` is stored encrypted in etcd: the stored value starts with the `aescbc` prefix and no longer holds the plain text code. The Secret still returns its original value through the API.
4. The API stays ready and both application replicas stay available.

## Verify The Result

The grader reads the API server pod, reads the stored value from etcd through the etcd pod, and reads the Secret through the API. Wait for the API server to restart before you submit. Keep a backup of the API server manifest outside `/etc/kubernetes/manifests`.
