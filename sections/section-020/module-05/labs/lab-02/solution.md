---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Remediate Five Kubelet Benchmark Findings Solution

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-05-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-05-02" || exit 1
node_name="astro-ats-031-lab-020-05-02-control-plane"
worker_name="astro-ats-031-lab-020-05-02-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Record the starting state

A remediation is easier to prove when you record the state before and after. This shell function prints the three fields from the effective configuration and the modes of the two files:

```sh
audit_kubelet() {
  kubectl get --raw "/api/v1/nodes/$worker_name/proxy/configz" | python3 -c 'import json, sys; settings = json.load(sys.stdin)["kubeletconfig"]; [print(key, settings.get(key)) for key in ("rotateCertificates", "streamingConnectionIdleTimeout", "tlsMinVersion")]'
  podman exec "$worker_name" stat -c '%a %U:%G %n' /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
}
audit_kubelet > kubelet-before.txt
cat kubelet-before.txt
```

`rotateCertificates` and `tlsMinVersion` print `None`, because the endpoint leaves out fields that are `false` or not set. The idle timeout prints `4h0m0s`: the kubelet treats `0s` as not set and uses its default. Both files have mode `644`.

## Fix the file modes

```sh
podman exec "$worker_name" chmod 600 /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
```

## Fix the three fields

The kubelet stops at start when a key appears twice, so delete each key before you add it. Keep a copy first:

```sh
podman exec "$worker_name" cp -p /var/lib/kubelet/config.yaml /root/kubelet-config.yaml.before
podman exec "$worker_name" sed -i -e '/^rotateCertificates:/d' -e '/^streamingConnectionIdleTimeout:/d' -e '/^tlsMinVersion:/d' /var/lib/kubelet/config.yaml
podman exec "$worker_name" sh -c "printf '\nrotateCertificates: true\nstreamingConnectionIdleTimeout: 5m\ntlsMinVersion: VersionTLS12\n' >> /var/lib/kubelet/config.yaml"
podman exec "$worker_name" systemctl restart kubelet
```

`rotateCertificates` renews the client certificate of the kubelet before it expires. `streamingConnectionIdleTimeout` closes `exec`, `attach` and `port-forward` connections that stay idle for five minutes. `tlsMinVersion` refuses TLS 1.0 and 1.1 on port `10250`.

## Prove the result

The kubelet reads its configuration only when it starts. Restart it, then read the effective configuration through the API server. The `configz` endpoint returns the values that the running kubelet really uses, after all sources are merged:

```sh
audit_kubelet > kubelet-after.txt
diff kubelet-before.txt kubelet-after.txt
kubectl get node "$worker_name"
```

The `diff` output shows each changed value: `True`, `5m0s`, `VersionTLS12` and mode `600` for both files. The node is `Ready`. If the old values still show, wait a few seconds and run `audit_kubelet` again.

## Common pitfalls

> [!WARNING]
> The idle timeout shows `5m0s` in `configz`, not `5m`. `chmod` on `config.yaml` with a restrictive mode does not stop the kubelet, because it runs as `root`. A duplicate key in `config.yaml` stops the kubelet; keep the copy so you can put it back.
