---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Enable Encryption At Rest For Secrets Solution

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-04-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-04-01" || exit 1
node_name="astro-ats-031-lab-020-04-01-control-plane"
worker_name="astro-ats-031-lab-020-04-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Inspect

Read the stored value of the Secret through the etcd pod before you change anything. The filter prints only a readable word:

```sh
kubectl -n kube-system exec "etcd-$node_name" -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get /registry/secrets/starfleet-031-020-04-01/launch-code --print-value-only | grep -a -o 'warp-nine-launch'
```

The word is readable, so the Secret is stored in clear text.

## Create the encryption configuration

Generate a random 32 byte key and copy the printed value:

```sh
head -c 32 /dev/urandom | base64
```

Save this as `encryption-config.yaml` and replace `<KEY>` with the value:

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

Copy the file to the control plane node and restrict its mode. Then copy the API server manifest to the host:

```sh
podman exec "$node_name" mkdir -p /etc/kubernetes/enc
podman cp encryption-config.yaml "$node_name:/etc/kubernetes/enc/encryption-config.yaml"
podman exec "$node_name" chmod 600 /etc/kubernetes/enc/encryption-config.yaml
podman cp "$node_name:/etc/kubernetes/manifests/kube-apiserver.yaml" kube-apiserver.yaml
```

## Edit the API server manifest

A copy of the original manifest is in `/opt/training/backup` on the node. In `kube-apiserver.yaml` on the host, add the flag under the container `command`, the mount under `volumeMounts` and the volume under `volumes`:

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

Install the file with `mv` so the kubelet never reads a half written file. Then wait until the new pod shows the flag:

```sh
podman cp kube-apiserver.yaml "$node_name:/root/kube-apiserver.yaml.new"
podman exec "$node_name" mv /root/kube-apiserver.yaml.new /etc/kubernetes/manifests/kube-apiserver.yaml
for attempt in $(seq 1 60); do
  if kubectl --request-timeout=3s -n kube-system get pod "kube-apiserver-$node_name" -o jsonpath='{.spec.containers[0].command}' 2>/dev/null | grep -q -e 'encryption-provider-config'; then echo "new flag visible"; break; fi
  sleep 3
done
```

If the loop never prints the message, read the kubelet log with `podman exec "$node_name" journalctl -u kubelet --no-pager -n 50`, or copy the backup in `/opt/training/backup` back into the manifests directory.

## Re-encrypt and verify

The existing Secret is still plain text, because the API server encrypts only on write. Replace every Secret unchanged:

```sh
kubectl get secrets --all-namespaces -o json | kubectl replace -f -
```

Read the stored value again. The filter now prints the encryption prefix, and a search for the plain text word finds nothing:

```sh
kubectl -n kube-system exec "etcd-$node_name" -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get /registry/secrets/starfleet-031-020-04-01/launch-code --print-value-only | grep -a -o 'k8s:enc:aescbc:v1:key1'
kubectl -n starfleet-031-020-04-01 get secret launch-code -o jsonpath='{.data.code}' | base64 -d
```

The first command prints the prefix. The second prints the original code, because the API server decrypts the value. Run `astrona submit` when both behave this way.
