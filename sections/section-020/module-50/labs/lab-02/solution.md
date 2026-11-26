# Remediate Five Kubelet Benchmark Findings — Solution

You solve this lab with one `chmod`, three fields in the kubelet configuration file and a kubelet restart. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

A remediation is easier to prove when you record the state before and after. This shell function prints the three fields from the effective configuration and the modes of the two files:

```sh
audit_kubelet() {
  kubectl get --raw "/api/v1/nodes/$(hostname)/proxy/configz" | python3 -c 'import json, sys; settings = json.load(sys.stdin)["kubeletconfig"]; [print(key, settings.get(key)) for key in ("rotateCertificates", "streamingConnectionIdleTimeout", "tlsMinVersion")]'
  sudo stat -c '%a %U:%G %n' /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
}
audit_kubelet > kubelet-before.txt
cat kubelet-before.txt
```

`rotateCertificates` and `tlsMinVersion` print `None`, because the endpoint leaves out fields that are `false` or not set. The idle timeout prints `4h0m0s`: the kubelet treats `0s` as not set and uses its default. Both files have mode `644`.

## Step 2: restrict the file modes (check `kubelet-file-modes`)

`config.yaml` holds the kubelet settings and `kubelet.conf` is the kubeconfig the kubelet uses to reach the API server. Only root needs to read them:

```sh
sudo chmod 600 /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
```

The kubelet runs as `root`, so the stricter mode does not stop it.

## Step 3: turn on certificate rotation (check `certificate-rotation`)

The kubelet stops at start when a key appears twice, so delete each key before you add it. Keep a copy first:

```sh
sudo cp -p /var/lib/kubelet/config.yaml /root/kubelet-config.yaml.before
sudo sed -i '/^rotateCertificates:/d' /var/lib/kubelet/config.yaml
sudo sh -c "printf '\nrotateCertificates: true\n' >> /var/lib/kubelet/config.yaml"
```

`rotateCertificates` renews the client certificate of the kubelet before it expires.

## Step 4: set the streaming idle timeout (check `streaming-idle-timeout`)

```sh
sudo sed -i '/^streamingConnectionIdleTimeout:/d' /var/lib/kubelet/config.yaml
sudo sh -c "printf '\nstreamingConnectionIdleTimeout: 5m\n' >> /var/lib/kubelet/config.yaml"
```

`streamingConnectionIdleTimeout` closes `exec`, `attach` and `port-forward` connections that stay idle for five minutes.

## Step 5: set the TLS minimum version (check `tls-min-version`)

```sh
sudo sed -i '/^tlsMinVersion:/d' /var/lib/kubelet/config.yaml
sudo sh -c "printf '\ntlsMinVersion: VersionTLS12\n' >> /var/lib/kubelet/config.yaml"
```

`tlsMinVersion` refuses TLS 1.0 and 1.1 on port `10250`. The end of the file now holds these lines, each once:

```yaml
rotateCertificates: true

streamingConnectionIdleTimeout: 5m

tlsMinVersion: VersionTLS12
```

The kubelet reads its configuration only when it starts, so restart it:

```sh
sudo systemctl restart kubelet
```

## Step 6: test the result

Read the effective configuration again through the API server. The `configz` endpoint returns the values that the running kubelet really uses, after all sources are merged:

```sh
audit_kubelet > kubelet-after.txt
diff kubelet-before.txt kubelet-after.txt
kubectl get node "$(hostname)"
```

The `diff` output shows each changed value: `True`, `5m0s`, `VersionTLS12` and mode `600` for both files. The node is `Ready`. If the old values still show, wait a few seconds and run `audit_kubelet` again.

## Step 7: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> The idle timeout shows `5m0s` in `configz`, not `5m`. A value other than five minutes fails the check.
>
> The grader reads the effective configuration, so a changed file without a kubelet restart changes nothing.
>
> A duplicate key in `config.yaml` stops the kubelet, and a node that is not `Ready` fails every check. Keep the copy so you can put it back.
