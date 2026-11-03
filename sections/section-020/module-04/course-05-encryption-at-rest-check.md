---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Encryption At Rest Check

By default the API server writes Secrets to etcd as plain text. Encryption at rest changes this: the API server encrypts the value before it writes and decrypts it when it reads. A stolen backup or disk copy then holds ciphertext, not credentials. The benchmark recommends it for Secrets. This part explains the configuration, enables it on the API server, and proves with etcd that it works.

## How the API server encrypts

The API server reads an `EncryptionConfiguration` file when it starts. The `--encryption-provider-config` flag gives the file path. The file lists the resources to encrypt, here `secrets`, and a list of providers in order.

Two rules decide the behavior. The first provider in the list encrypts every new write. When the API server reads a value, it tries each provider in order until one of them can decode it. A provider called `identity` stores data without encryption. If you put `identity` last, the API server can still read old plain text values, and the first provider encrypts all new writes.

The `aescbc` provider uses AES in CBC mode with a 32 byte key. Other providers are `aesgcm`, `secretbox` and a `kms` provider, where an external Key Management Service holds the key. The Kubernetes documentation prefers `secretbox` or the KMS provider over `aescbc` for new setups, and this course uses `aescbc` because the benchmark and the exam mention it. The key is the weak point of every local provider: it sits in a file on the control plane node, so protect that file with mode `600` and keep a copy of the key. If you lose the key, the encrypted Secrets cannot be read.

## Save the configuration

Generate a random 32 byte key and print it as base64 text. The value goes into the file in the next step:

<!-- astrona:playground:renew -->

```sh
head -c 32 /dev/urandom | base64
```

Copy the printed value. Save this as `encryption-config.yaml` and replace `<KEY>` with it:

```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: <KEY>
      - identity: {}
```

The name `key1` is a label that the API server stores with each encrypted value, so a later key rotation can tell which key was used. Never store this file in a shared place, because it holds the key.

## Place the file on the node

The API server runs as a container, so it can read only paths that its pod mounts. Copy the file to the control plane node, restrict its mode, and make a copy of the API server manifest on the host to edit:

```sh
NODE=astro-ats-031-playground-020-04-control-plane
podman exec $NODE mkdir -p /etc/kubernetes/enc
podman cp encryption-config.yaml $NODE:/etc/kubernetes/enc/encryption-config.yaml
podman exec $NODE chmod 600 /etc/kubernetes/enc/encryption-config.yaml
podman cp $NODE:/etc/kubernetes/manifests/kube-apiserver.yaml kube-apiserver.yaml
```

A copy of the original manifest is already in `/opt/training/backup` on the node. Keep any other backup outside `/etc/kubernetes/manifests`, because the kubelet starts a pod from every file in that directory.

## Edit the API server manifest

Open `kube-apiserver.yaml` on the host and make three additions. The flag goes under the container `command`. The volume mount goes under the container `volumeMounts`. The volume goes under the pod `volumes`. Keep the indentation of the neighbouring lines.

```yaml
# under spec.containers[0].command
    - --encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml

# under spec.containers[0].volumeMounts
    - mountPath: /etc/kubernetes/enc
      name: enc
      readOnly: true

# under spec.volumes
  - hostPath:
      path: /etc/kubernetes/enc
      type: DirectoryOrCreate
    name: enc
```

Install the edited file. The copy goes to `/root` first and `mv` places it in the manifests directory in one step, so the kubelet never reads a half written file. Then wait until the new API server pod shows the flag. `kubectl` fails while the API server restarts, so the loop ignores errors and tries again, at most 60 times:

```sh
podman cp kube-apiserver.yaml $NODE:/root/kube-apiserver.yaml.new
podman exec $NODE mv /root/kube-apiserver.yaml.new /etc/kubernetes/manifests/kube-apiserver.yaml
for attempt in $(seq 1 60); do
  if kubectl --request-timeout=3s -n kube-system get pod kube-apiserver-$NODE -o jsonpath='{.spec.containers[0].command}' 2>/dev/null | grep -q -e 'encryption-provider-config'; then echo "new flag visible"; break; fi
  sleep 3
done
```

If the loop never prints the message, the API server did not start with the new file. The usual causes are an indentation mistake or a wrong path. Read the kubelet log with `podman exec $NODE journalctl -u kubelet --no-pager -n 50`, or put the staged backup back into the manifests directory.

## Prove it with etcd

The existing Secret `launch-code` is still plain text, because the API server encrypts only on write. A new Secret is the first test. Create one and read its value from etcd. The `grep` prints the prefix that the encryption provider adds to every value it encrypts:

```sh
kubectl -n starfleet create secret generic dock-code --from-literal=code=warp-nine-dock
ETCD_POD=etcd-$NODE
kubectl -n kube-system exec $ETCD_POD -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get /registry/secrets/starfleet/dock-code --print-value-only | grep -a -o 'k8s:enc:aescbc:v1:key1'
```

The command prints `k8s:enc:aescbc:v1:key1`, which shows that this value is stored with the `aescbc` provider and `key1`. A search for `warp-nine-dock` in the same output finds nothing. Run the same read for `launch-code` and the plain word `warp-nine-launch` is still there.

## Re-encrypt the existing Secrets

To encrypt the old values, read every Secret through the API server and write it back unchanged. Each write goes through the first provider:

```sh
kubectl get secrets --all-namespaces -o json | kubectl replace -f -
```

Run the etcd read for `launch-code` again. It now starts with the `aescbc` prefix, and the plain word is gone. The API still returns the original value, because the API server decrypts it. Only after this step do you have encryption at rest for the old data.

The common check for this setting is a flag in the pod and a ciphertext prefix in etcd. A flag without the prefix proves nothing, because the API server could be using the file in a way that does not cover `secrets`.

## Limits

Encryption at rest protects a copy of the etcd data. It does not protect the Secrets from someone who can read the key file on the control plane node, from an RBAC role that allows `get secrets`, or from a process in the API server. It also does not cover other resources unless you list them under `resources`. A new key later needs a rotation: add the new key first, restart, replace all Secrets, then remove the old key.

## Common pitfalls

> [!WARNING]
> - **Putting `identity` first.** The first provider encrypts new writes. With `identity` first nothing is encrypted, although the API server starts normally.
> - **Skipping the volume mount.** The API server pod cannot read a file outside its mounts, and it fails to start with a missing file error.
> - **Forgetting to re-encrypt.** Existing Secrets stay plain text until they are written again.
> - **Removing the old key too early.** Remove it only after all Secrets are rewritten with the new one, or the API server cannot read the old values.
> - **Losing the key.** There is no recovery. Keep a protected copy outside the cluster.
