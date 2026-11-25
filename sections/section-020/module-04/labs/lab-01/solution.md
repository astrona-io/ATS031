---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Enable Encryption At Rest For Secrets Solution

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-04-01
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-04-01`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## See the plain text in etcd

Read the stored value of the Secret through `etcdctl` in the etcd pod. The `grep -a -o` filter prints only the readable word from the binary value:

```sh
kubectl -n kube-system exec "etcd-astro-ats-031-lab-020-04-01" -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get /registry/secrets/starfleet-031-020-04-01/launch-code --print-value-only | grep -a -o 'warp-nine-launch'
```

The word appears, so etcd stores the value as plain text. Base64 in the API is only an encoding, not encryption.

## Write the encryption configuration

An `EncryptionConfiguration` tells the API server how to encrypt each resource type before it writes the object to etcd. The first provider in the list encrypts new writes. All providers in the list can decrypt. `identity` means no encryption; it stays last so that the API server can still read objects that were written before the change. Generate a random 32 byte key:

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

## Edit the API server manifest

The kubelet watches `/etc/kubernetes/manifests` and starts every file in it as a static pod. Edit a copy in a work directory outside that folder and move it back in one step, so that the kubelet never reads a half-written file:

```sh
sudo mkdir -p /etc/kubernetes/edit
sudo cp -p /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/edit/kube-apiserver.yaml
sudo vi /etc/kubernetes/edit/kube-apiserver.yaml
```

Add the flag to the `command` list, the mount under `volumeMounts:` of the container, and the volume under `volumes:` of the pod:

```yaml
    - --encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml
```

```yaml
    - mountPath: /etc/kubernetes/enc
      name: enc
      readOnly: true
```

```yaml
  - hostPath:
      path: /etc/kubernetes/enc
      type: DirectoryOrCreate
    name: enc
```

Save the file and move it back:

```sh
sudo mv /etc/kubernetes/edit/kube-apiserver.yaml /etc/kubernetes/manifests/kube-apiserver.yaml
```

## Rewrite the Secrets and check

Wait until the new API server is ready. The API server encrypts only on write, so the existing Secret is still plain text. Replace every Secret without a change, so that the API server writes each one again:

```sh
for attempt in $(seq 1 60); do
  if sudo ps -eo args | grep '^kube-apiserver ' | grep -q -e '--encryption-provider-config' && kubectl --request-timeout=3s get --raw=/readyz >/dev/null 2>&1; then echo "new flag visible and API server ready"; break; fi
  sleep 3
done
```

The old API server process can still answer for a few seconds after the `mv`, so the loop waits until the running API server process has the new flag and the API server is ready. It prints `new flag visible and API server ready`. If it ends without that message, run `sudo crictl ps -a --name kube-apiserver` and read the logs of the exited container.

```sh
kubectl get secrets --all-namespaces -o json | kubectl replace -f -
```

Read the stored value again, and read the Secret through the API:

```sh
kubectl -n kube-system exec "etcd-astro-ats-031-lab-020-04-01" -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get /registry/secrets/starfleet-031-020-04-01/launch-code --print-value-only | grep -a -o 'k8s:enc:aescbc:v1:key1'
kubectl -n starfleet-031-020-04-01 get secret launch-code -o jsonpath='{.data.code}' | base64 -d
```

The first command prints the prefix `k8s:enc:aescbc:v1:key1`: the provider, its version and the key name. The second command prints `warp-nine-launch`, because the API server decrypts the value for authorized clients.

## Common pitfalls

> [!WARNING]
> With `identity` first, the API server keeps writing plain text, even with an `aescbc` entry below it. Without the volume, the API server cannot find the file and does not start. Existing Secrets stay plain text until they are written again. Losing the key makes every encrypted Secret unreadable.
