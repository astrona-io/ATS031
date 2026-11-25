# Encryption At Rest Check

By default, the API server writes Secrets to etcd as plain text. Encryption at rest changes this. The API server encrypts the value before it writes it to etcd, and decrypts it when it reads it back. A stolen backup or disk copy then holds ciphertext (encrypted data), not credentials.

The Center for Internet Security (CIS) Kubernetes Benchmark, a list of checks for a secure cluster, recommends encryption at rest for Secrets. On this page, you learn how the configuration works, enable it on the API server, and prove with etcd that it works.

## How the API server encrypts

The API server reads an `EncryptionConfiguration` file when it starts. The `--encryption-provider-config` flag gives the path of this file. The file lists the resources to encrypt, here `secrets`, and a list of providers in order. A provider is one method to store the data, with or without encryption.

Two rules decide the behavior:

- The first provider in the list encrypts every new write.
- When the API server reads a value, it tries each provider in order until one of them can decode the value.

A provider called `identity` stores data without encryption. If you put `identity` last, the API server can still read old plain text values, and the first provider encrypts all new writes.

![Diagram: on a write, provider 1 aescbc with key1 encrypts the new Secret dock-code and etcd stores it with the prefix k8s:enc:aescbc:v1:key1; on a read of the old plain value of launch-code, aescbc is skipped, identity reads the value, and the API server gets it](images/encryption-provider-order.svg)

The drawing shows both rules with the two Secrets of this page. A new write always goes through the first provider. An old plain value is still readable, because `identity` comes later in the list.

The `aescbc` provider uses the Advanced Encryption Standard (AES) in cipher block chaining (CBC) mode with a 32 byte key. Other providers are `aesgcm`, `secretbox` and a `kms` provider, where an external Key Management Service (KMS) holds the key. The Kubernetes documentation prefers `secretbox` or the KMS provider over `aescbc` for new setups. This course uses `aescbc` because the benchmark and the exam mention it.

The key is the weak point of every local provider. It sits in a file on the control plane node, so protect that file with mode `600` and keep a copy of the key. If you lose the key, nobody can read the encrypted Secrets.

## Save the configuration

Open a shell on the node. Generate a random 32 byte key and print it as base64 text. The value goes into the file in the next step:

<!-- astrona:playground:renew -->

```sh
astrona ssh astro-ats-031-playground-020-04
head -c 32 /dev/urandom | base64
```

The output is one line of 44 characters that ends with `=`. Copy the printed value. Save this as `encryption-config.yaml` in your home directory on the node, and replace `<KEY>` with the value. The node has the editors `nano` and `vi`.

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

The name `key1` is a label that the API server stores with each encrypted value. During a later key rotation, this label tells the API server which key encrypted a value. Never store this file in a shared place, because it holds the key.

## Place the file on the node

The API server runs as a container, so it can read only the paths that its pod mounts. The next commands copy the file to a new directory `/etc/kubernetes/enc` and restrict its mode. They also make a copy of the API server manifest in your home directory for you to edit. Only `root` can read the manifest, so `sudo cat` reads it, and the shell writes the copy as your own file:

```sh
sudo mkdir -p /etc/kubernetes/enc
sudo cp encryption-config.yaml /etc/kubernetes/enc/encryption-config.yaml
sudo chmod 600 /etc/kubernetes/enc/encryption-config.yaml
sudo ls -l /etc/kubernetes/enc
sudo cat /etc/kubernetes/manifests/kube-apiserver.yaml > kube-apiserver.yaml
```

The `ls` line shows `-rw------- 1 root root` for `encryption-config.yaml`, so only `root` can read the key.

A copy of the original manifest is already in `/opt/training/backup` on the node. Keep any other backup outside `/etc/kubernetes/manifests`, because the kubelet starts a pod from every file in that directory. Hidden files are the exception. The kubelet ignores files whose names start with a dot, such as the empty `.kubelet-keep` file that the package put there.

## Edit the API server manifest

Open `kube-apiserver.yaml` in your home directory with `nano` or `vi`, and make three additions:

- The flag goes under the container `command`, for example right after the line `- kube-apiserver`.
- The volume mount goes under the container `volumeMounts`.
- The volume goes under the pod `volumes`.

Keep the indentation of the lines next to each addition.

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

![Diagram: the file /etc/kubernetes/enc/encryption-config.yaml with mode 600 lies on the node, the hostPath volume enc brings the directory into the kube-apiserver pod, the container mounts it read-only at /etc/kubernetes/enc, and the --encryption-provider-config flag names the file](images/encryption-config-mount.svg)

The drawing shows why all three additions are needed. The volume brings the node directory into the pod, the mount puts it inside the container, and only then can the flag point at a file the API server can open.

Now install the edited file. The copy goes to `/root` first, `chmod` gives it the mode `600` of the original manifest, and `mv` places it in the manifests directory in one step. This way, the kubelet never reads a half-written file.

Then wait until the pod object of the new API server shows the flag, and the API server reports that it is ready. The pod object can show the new flag a few seconds before the new API server is ready, so the loop checks both. `kubectl` fails while the API server restarts, so the loop ignores errors and tries again, at most 60 times:

```sh
NODE=astro-ats-031-playground-020-04
sudo cp kube-apiserver.yaml /root/kube-apiserver.yaml.new
sudo chmod 600 /root/kube-apiserver.yaml.new
sudo mv /root/kube-apiserver.yaml.new /etc/kubernetes/manifests/kube-apiserver.yaml
for attempt in $(seq 1 60); do
  if kubectl --request-timeout=3s -n kube-system get pod kube-apiserver-$NODE -o jsonpath='{.spec.containers[0].command}' 2>/dev/null | grep -q -e 'encryption-provider-config' && kubectl --request-timeout=3s get --raw=/readyz >/dev/null 2>&1; then echo "new flag visible and API server ready"; break; fi
  sleep 3
done
```

The loop prints `new flag visible and API server ready`. On the playground node, this took about 45 seconds; a restart of the API server can take between 40 and 70 seconds there.

If the loop never prints the message, the API server did not start with the new file. The usual causes are an indentation mistake or a wrong path. Read the kubelet log with `sudo journalctl -u kubelet --no-pager -n 50`, or copy `/opt/training/backup/kube-apiserver.yaml` back into the manifests directory with `sudo cp`.

## Prove it with etcd

A running API server with the new flag is not yet a proof. The existing Secret `launch-code` is still plain text, because the API server encrypts only on write. So the first test is a new Secret.

Create one and read its value from etcd. The `grep` prints the prefix that the encryption provider adds to every value it encrypts:

```sh
kubectl -n starfleet create secret generic dock-code --from-literal=code=warp-nine-dock
ETCD_POD=etcd-$NODE
kubectl -n kube-system exec $ETCD_POD -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get /registry/secrets/starfleet/dock-code --print-value-only | grep -a -o 'k8s:enc:aescbc:v1:key1'
```

The output is:

```text
secret/dock-code created
k8s:enc:aescbc:v1:key1
```

The prefix `k8s:enc:aescbc:v1:key1` shows that this value is stored with the `aescbc` provider and `key1`. A search for `warp-nine-dock` in the same output finds nothing. Run the same read for `launch-code` with `grep -a -o 'warp-nine-launch'`, and the plain word is still there.

## Re-encrypt the existing Secrets

To encrypt the old values, read every Secret through the API server and write it back unchanged. Each write goes through the first provider:

```sh
kubectl get secrets --all-namespaces -o json | kubectl replace -f -
```

The output on the playground node (the name of the bootstrap token differs on your node):

```text
secret/bootstrap-token-rrlue1 replaced
secret/dock-code replaced
secret/launch-code replaced
```

Run the etcd read for `launch-code` again, this time with `grep -a -o -e 'k8s:enc:aescbc:v1:key1' -e 'warp-nine-launch'`. It now prints only `k8s:enc:aescbc:v1:key1`. The value starts with the `aescbc` prefix, and the plain word is gone.

The API still returns the original value, because the API server decrypts it. Only after this step is the old data encrypted at rest too.

The usual check for this setting looks for two things: the flag in the pod, and the ciphertext prefix in etcd. A flag without the prefix proves nothing, because the API server could use the file in a way that does not cover `secrets`. kube-bench, the tool that checks a node against the benchmark, shows the same gap. Its check `1.2.27` on the playground node passes as soon as the flag is set, and it does not read etcd.

## Limits

Encryption at rest protects a copy of the etcd data. It does not protect the Secrets from:

- someone who can read the key file on the control plane node;
- a role-based access control (RBAC) role that allows `get secrets`;
- a process in the API server.

It also does not cover other resources, unless you list them under `resources`. A new key later needs a rotation: add the new key first, restart, replace all Secrets, then remove the old key.

You can now turn on encryption at rest, roll it out to the existing Secrets, and prove the result in etcd instead of trusting the flag. The question that stays open is the key itself: who can read the key file, and how you rotate the key without losing access to old values.

## Common pitfalls

> [!WARNING]
> - **Putting `identity` first.** The first provider encrypts new writes. With `identity` first, nothing is encrypted, although the API server starts normally.
> - **Skipping the volume mount.** The API server pod cannot read a file outside its mounts, and it fails to start with a missing file error.
> - **Forgetting to re-encrypt.** Existing Secrets stay plain text until they are written again.
> - **Removing the old key too early.** Remove it only after all Secrets are rewritten with the new key, or the API server cannot read the old values.
> - **Losing the key.** There is no recovery. Keep a protected copy outside the cluster.
