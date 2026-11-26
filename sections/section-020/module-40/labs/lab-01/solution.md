# Enable Encryption At Rest For Secrets — Solution

You solve this lab with one file on the control plane node, one change to the API server manifest and one rewrite of the Secrets. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

etcd runs as a static pod named after the node. Read the stored value of the Secret through `etcdctl` in the etcd pod. The `grep -a -o` filter prints only the readable word from the binary value:

```sh
kubectl -n kube-system exec "etcd-$(hostname)" -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get /registry/secrets/starfleet-031-020-04-01/launch-code --print-value-only | grep -a -o 'warp-nine-launch'
sudo ls /etc/kubernetes/manifests
```

The first command prints `warp-nine-launch`, so etcd stores the value as plain text. Base64 in the API is only an encoding, not encryption. The manifests folder holds the four control plane manifests: `etcd.yaml`, `kube-apiserver.yaml`, `kube-controller-manager.yaml` and `kube-scheduler.yaml`.

## Step 2: write the encryption configuration (check `encryption-config`)

An `EncryptionConfiguration` tells the API server how to encrypt each resource type before it writes the object to etcd. The first provider in the list encrypts new writes. All providers in the list can decrypt. `identity` means no encryption; it stays last so that the API server can still read objects that were written before the change.

Generate a random 32 byte key:

```sh
head -c 32 /dev/urandom | base64
```

Save this as `encryption-config.yaml`, and replace `<KEY>` with the printed value:

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

Copy the file to the folder that the API server will read and restrict its mode, because the key in it decrypts every Secret:

```sh
sudo mkdir -p /etc/kubernetes/enc
sudo cp encryption-config.yaml /etc/kubernetes/enc/encryption-config.yaml
sudo chmod 600 /etc/kubernetes/enc/encryption-config.yaml
```

## Step 3: point the API server at the file (check `encryption-provider`)

The kubelet watches `/etc/kubernetes/manifests` and starts every file in it as a static pod. Edit a copy in a work directory outside that folder and move it back in one step, so that the kubelet never reads a half-written file:

```sh
sudo mkdir -p /etc/kubernetes/edit
sudo cp -p /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/edit/kube-apiserver.yaml
sudo vi /etc/kubernetes/edit/kube-apiserver.yaml
```

Make three additions. Add the flag to the `command` list, right after the line `- kube-apiserver`:

```yaml
    - --encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml
```

Add the mount as the first item under `volumeMounts:` of the container:

```yaml
    - mountPath: /etc/kubernetes/enc
      name: enc
      readOnly: true
```

Add the volume as the first item under `volumes:` of the pod:

```yaml
  - hostPath:
      path: /etc/kubernetes/enc
      type: DirectoryOrCreate
    name: enc
```

Without the volume, the API server container cannot see the file and does not start. Save the file and move it back:

```sh
sudo mv /etc/kubernetes/edit/kube-apiserver.yaml /etc/kubernetes/manifests/kube-apiserver.yaml
```

The old API server process can still answer for a few seconds after the `mv`. Wait until the running process has the new flag and the API server is ready:

```sh
for attempt in $(seq 1 60); do
  if sudo ps -eo args | grep '^kube-apiserver ' | grep -q -e '--encryption-provider-config' && kubectl --request-timeout=3s get --raw=/readyz >/dev/null 2>&1; then echo "new flag visible and API server ready"; break; fi
  sleep 3
done
```

The loop prints `new flag visible and API server ready`. If it ends without that message, run `sudo crictl ps -a --name kube-apiserver` and read the logs of the exited container.

## Step 4: rewrite the Secrets (check `secret-encrypted`)

The API server encrypts only on write, so the existing Secret is still plain text in etcd. Replace every Secret without a change, so that the API server writes each one again:

```sh
kubectl get secrets --all-namespaces -o json | kubectl replace -f -
```

## Step 5: test the result

Read the stored value again, and read the Secret through the API:

```sh
kubectl -n kube-system exec "etcd-$(hostname)" -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get /registry/secrets/starfleet-031-020-04-01/launch-code --print-value-only | grep -a -o 'k8s:enc:aescbc:v1:key1'
kubectl -n starfleet-031-020-04-01 get secret launch-code -o jsonpath='{.data.code}' | base64 -d
sudo stat -c '%a' /etc/kubernetes/enc/encryption-config.yaml
```

The first command prints `k8s:enc:aescbc:v1:key1`: the provider, its version and the key name. The second prints `warp-nine-launch`, because the API server decrypts the value for authorized clients. The third prints `600`.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> With `identity` first, the API server keeps writing plain text, even with an `aescbc` entry below it. The key must decode to exactly 32 bytes; a short or hand-typed key fails.
>
> Existing Secrets stay plain text until they are written again, so the flag alone does not pass `secret-encrypted`.
>
> Do not leave a backup or a spare copy in `/etc/kubernetes/manifests`. The kubelet starts every file there, and the grader accepts only the four control plane manifests.
