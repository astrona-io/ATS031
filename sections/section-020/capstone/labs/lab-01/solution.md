---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Remediate A CIS Benchmark Review Solution

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-capstone-020)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-capstone-020" || exit 1
node_name="astro-ats-031-capstone-020-control-plane"
worker_name="astro-ats-031-capstone-020-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Record the starting state

Capture the values you will compare later. The commands read the API server flags, the etcd directory mode and the effective kubelet settings:

```sh
kubectl -n kube-system get pod "kube-apiserver-$node_name" -o jsonpath='{.spec.containers[0].command}' | tr ',' '\n' | grep -e profiling -e encryption
podman exec "$node_name" stat -c '%a %n' /var/lib/etcd
kubectl get --raw "/api/v1/nodes/$worker_name/proxy/configz" | python3 -m json.tool | grep -e anonymous -e '"mode"' -e readOnlyPort
```

The API server has no `--profiling=false` and no encryption flag, the data directory has mode `755`, and the kubelet shows anonymous access enabled, mode `AlwaysAllow` and port `10255`.

## Fix etcd permissions

The permission fix does not restart anything:

```sh
podman exec "$node_name" chmod 700 /var/lib/etcd
podman exec "$node_name" stat -c '%a %n' /var/lib/etcd
```

## Fix the API server

Two changes go into the same static pod manifest: the profiling flag and the encryption configuration. Generate a key and copy the printed value:

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

Copy it to the control plane node and copy the API server manifest to the host:

```sh
podman exec "$node_name" mkdir -p /etc/kubernetes/enc
podman cp encryption-config.yaml "$node_name:/etc/kubernetes/enc/encryption-config.yaml"
podman exec "$node_name" chmod 600 /etc/kubernetes/enc/encryption-config.yaml
podman cp "$node_name:/etc/kubernetes/manifests/kube-apiserver.yaml" kube-apiserver.yaml
```

In `kube-apiserver.yaml` add the two flags under the container `command`, the mount under `volumeMounts` and the volume under `volumes`:

```yaml
# under spec.containers[0].command
    - --profiling=false
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

Install the file with `mv` and wait until the new pod shows both flags and the API is ready:

```sh
podman cp kube-apiserver.yaml "$node_name:/root/kube-apiserver.yaml.new"
podman exec "$node_name" mv /root/kube-apiserver.yaml.new /etc/kubernetes/manifests/kube-apiserver.yaml
for attempt in $(seq 1 80); do
  if kubectl --request-timeout=3s -n kube-system get pod "kube-apiserver-$node_name" -o jsonpath='{.spec.containers[0].command}' 2>/dev/null | grep -q -e 'encryption-provider-config' && kubectl --request-timeout=3s get --raw=/readyz >/dev/null 2>&1; then echo "ready"; break; fi
  sleep 3
done
```

If the loop never prints the message, read the kubelet log with `podman exec "$node_name" journalctl -u kubelet --no-pager -n 50` or copy the backup from `/opt/training/backup` back into the manifests directory.

Then encrypt the existing Secrets by writing them back unchanged:

```sh
kubectl get secrets --all-namespaces -o json | kubectl replace -f -
kubectl -n kube-system exec "etcd-$node_name" -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get /registry/secrets/starfleet/launch-code --print-value-only | grep -a -o 'k8s:enc:aescbc:v1:key1'
```

The second command prints the prefix.

## Fix the kubelet

Change the two existing lines, remove the old `readOnlyPort` line and append a new one so the key appears once. Then restart the kubelet and wait for the effective configuration:

```sh
podman exec "$worker_name" sed -i '/^  anonymous:/{n;s/enabled: true/enabled: false/}' /var/lib/kubelet/config.yaml
podman exec "$worker_name" sed -i 's/^  mode: AlwaysAllow$/  mode: Webhook/' /var/lib/kubelet/config.yaml
podman exec "$worker_name" sed -i '/^readOnlyPort:/d' /var/lib/kubelet/config.yaml
podman exec "$worker_name" sh -c "printf '\nreadOnlyPort: 0\n' >> /var/lib/kubelet/config.yaml"
podman exec "$worker_name" systemctl restart kubelet
for attempt in $(seq 1 60); do
  if kubectl --request-timeout=3s get --raw "/api/v1/nodes/$worker_name/proxy/configz" 2>/dev/null | grep -q '"anonymous":{"enabled":false}'; then echo "settled"; break; fi
  sleep 3
done
```

## Record the evidence

Save this as `configmap-cis-evidence.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cis-evidence
  namespace: starfleet
data:
  apiserver-profiling: fixed
  etcd-data-dir: fixed
  etcd-encryption: fixed
  kubelet-anonymous-auth: fixed
  kubelet-authorization-mode: fixed
  kubelet-read-only-port: fixed
  before: "profiling enabled, data directory 755, Secrets in clear text, kubelet anonymous AlwaysAllow port 10255"
  after: "profiling disabled, data directory 700, Secrets encrypted, kubelet anonymous off Webhook port closed"
```

Apply it:

```sh
kubectl apply -f configmap-cis-evidence.yaml
```

Then check the result:

```sh
kubectl -n starfleet get configmap cis-evidence
kubectl -n starfleet get deployment probe
kubectl get node "$worker_name"
```

The ConfigMap exists, the Deployment has two ready replicas and the node is `Ready`. Run `astrona submit` when all six findings are fixed.
