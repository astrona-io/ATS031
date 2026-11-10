---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Enable Encryption At Rest For Secrets

Solve this question on: `terminal`

The security team found that the Secret `launch-code` in `starfleet-031-020-04-01` is stored in clear text in etcd, the key-value store of the cluster. Enable encryption at rest for Secrets without stopping the cluster. The environment has two healthy `probe` replicas, an internal Service, two client pods and the Secret `launch-code`. The API server runs as a static pod and has no encryption configuration. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

Use a host shell with the private kubeconfig for this independent kind environment.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-04-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-04-01" || exit 1
node_name="astro-ats-031-lab-020-04-01-control-plane"
worker_name="astro-ats-031-lab-020-04-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

Allow about 12 minutes for task work. Cluster startup adds time.

## Tasks

1. Create the file `/etc/kubernetes/enc/encryption-config.yaml` on the control plane node with mode `600`. It holds an `EncryptionConfiguration` for `secrets` with the `aescbc` provider first and the `identity` provider last.
2. Make the `kube-apiserver` static pod run with `--encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml`, and mount the file into the pod. Wait until the API server answers `ok` on `/readyz`.
3. Rewrite the Secret `launch-code`, so that it is stored again with the new provider. The stored value in etcd must start with the `aescbc` prefix and must no longer hold the plain text code.

## Constraints

- The Secret `launch-code` must still return its original value through the API.
- Keep the API ready and both application replicas available.
- Keep a backup of the API server manifest outside `/etc/kubernetes/manifests`.

## How the answer is checked

The grader runs two checks. The first reads the command of the running API server pod and needs `--encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml` in it. The second reads the stored value of `/registry/secrets/starfleet-031-020-04-01/launch-code` from etcd through the etcd pod, and needs the prefix `k8s:enc:aescbc:v1:` and no plain text code in it. Both checks also need the Secret to return its original value through the API, `/readyz` to return `ok`, the `probe` Deployment fully rolled out, the `shuttle` pod running and ready, and a response with `version=v1` when `shuttle` requests `http://probe/`.

Hint: `kubectl replace` with the output of `kubectl get secret -o json` writes the Secret again.
