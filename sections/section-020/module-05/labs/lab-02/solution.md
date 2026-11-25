---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Remediate Five Kubelet Benchmark Findings Solution

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-05-02
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-05-02`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Record the starting state

A remediation is easier to prove when you record the state before and after. This shell function prints the three fields from the effective configuration and the modes of the two files:

```sh
audit_kubelet() {
  kubectl get --raw "/api/v1/nodes/astro-ats-031-lab-020-05-02/proxy/configz" | python3 -c 'import json, sys; settings = json.load(sys.stdin)["kubeletconfig"]; [print(key, settings.get(key)) for key in ("rotateCertificates", "streamingConnectionIdleTimeout", "tlsMinVersion")]'
  sudo stat -c '%a %U:%G %n' /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
}
audit_kubelet > kubelet-before.txt
cat kubelet-before.txt
```

`rotateCertificates` and `tlsMinVersion` print `None`, because the endpoint leaves out fields that are `false` or not set. The idle timeout prints `4h0m0s`: the kubelet treats `0s` as not set and uses its default. Both files have mode `644`.

## Fix the file modes

```sh
sudo chmod 600 /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
```

## Fix the three fields

The kubelet stops at start when a key appears twice, so delete each key before you add it. Keep a copy first:

```sh
sudo cp -p /var/lib/kubelet/config.yaml /root/kubelet-config.yaml.before
sudo sed -i -e '/^rotateCertificates:/d' -e '/^streamingConnectionIdleTimeout:/d' -e '/^tlsMinVersion:/d' /var/lib/kubelet/config.yaml
sudo sh -c "printf '\nrotateCertificates: true\nstreamingConnectionIdleTimeout: 5m\ntlsMinVersion: VersionTLS12\n' >> /var/lib/kubelet/config.yaml"
sudo systemctl restart kubelet
```

`rotateCertificates` renews the client certificate of the kubelet before it expires. `streamingConnectionIdleTimeout` closes `exec`, `attach` and `port-forward` connections that stay idle for five minutes. `tlsMinVersion` refuses TLS 1.0 and 1.1 on port `10250`.

## Prove the result

The kubelet reads its configuration only when it starts. Restart it, then read the effective configuration through the API server. The `configz` endpoint returns the values that the running kubelet really uses, after all sources are merged:

```sh
audit_kubelet > kubelet-after.txt
diff kubelet-before.txt kubelet-after.txt
kubectl get node "astro-ats-031-lab-020-05-02"
```

The `diff` output shows each changed value: `True`, `5m0s`, `VersionTLS12` and mode `600` for both files. The node is `Ready`. If the old values still show, wait a few seconds and run `audit_kubelet` again.

## Common pitfalls

> [!WARNING]
> The idle timeout shows `5m0s` in `configz`, not `5m`. `chmod` on `config.yaml` with a restrictive mode does not stop the kubelet, because it runs as `root`. A duplicate key in `config.yaml` stops the kubelet; keep the copy so you can put it back.
