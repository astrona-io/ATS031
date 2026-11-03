---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Read-Only Port, Ports And TLS Settings

Closing the authenticated API is not enough if a second listener answers without authentication. The kubelet has a read-only HTTP port that does exactly this. This part finds that port, shows what it exposes, closes it, and then reviews the Transport Layer Security (TLS) and certificate rotation settings of the main kubelet port.

## The ports of the kubelet

The kubelet listens on several ports. Port `10250` is the HTTPS API, protected by the authentication and authorization settings. Port `10248` is a health check on the loopback address. Port `10255` is the read-only port. It serves plain HTTP with no authentication and no encryption, and it exposes information such as the list of pods and the metrics of the node. The field `readOnlyPort` in the kubelet configuration controls it, and the value `0` disables the port. The benchmark requires that the port is disabled. Newer kubelet versions default to disabled, and the playground opens it on purpose.

## Show the exposure

The `shuttle` pod is a client pod in the cluster. Pods can reach the IP address of a node, so a compromised pod could read this port. The command below sends a request from `shuttle` to port `10255` of the worker:

<!-- astrona:playground:renew -->

```sh
WORKER=astro-ats-031-playground-020-05-worker
WORKER_IP=$(kubectl get node $WORKER -o jsonpath='{.status.addresses[?(@.type=="InternalIP")].address}')
kubectl -n starfleet exec shuttle -- wget -q -T 3 -O- http://$WORKER_IP:10255/pods
```

The output is a JSON document that lists the pods of the node, including their images, environment variable names and volumes. The request carried no credentials and no certificate. The same request to a closed port fails after the time limit of three seconds.

## Close the port

The key must exist only once, so the commands remove any existing line and append the new one. A blank line before the new key protects against a file that does not end with a line break:

```sh
podman exec $WORKER cp /var/lib/kubelet/config.yaml /root/kubelet-config.yaml.bak
podman exec $WORKER sed -i '/^readOnlyPort:/d' /var/lib/kubelet/config.yaml
podman exec $WORKER sh -c "printf '\nreadOnlyPort: 0\n' >> /var/lib/kubelet/config.yaml"
podman exec $WORKER grep -n 'readOnlyPort' /var/lib/kubelet/config.yaml
podman exec $WORKER systemctl restart kubelet
```

The `grep` shows exactly one line with `readOnlyPort: 0`. After the restart, repeat the request from `shuttle`. It now fails with a timeout or a connection error, and `wget` exits with a nonzero status. Wait for the kubelet to restart before you judge: run the request again after about ten seconds if it still answers.

## TLS settings of port 10250

Three fields in the file shape the TLS connection of port `10250`.

- `tlsMinVersion` sets the lowest TLS version the kubelet accepts. The value `VersionTLS12` or higher removes old protocol versions. If the field is empty, the Go library default applies, which recent versions set to TLS 1.2 for servers.
- `tlsCipherSuites` lists the allowed cipher suites. The benchmark asks for a list of strong ciphers, and a restricted list limits the kubelet to those. A list that is too narrow can stop clients from connecting, so test after a change.
- `tlsCertFile` and `tlsPrivateKeyFile` name the serving certificate. If they are empty, the kubelet creates a self-signed certificate, which clients cannot verify.

Set the minimum version with the same remove-and-append routine, and check the effective value after the restart:

```sh
podman exec $WORKER sed -i '/^tlsMinVersion:/d' /var/lib/kubelet/config.yaml
podman exec $WORKER sh -c "printf '\ntlsMinVersion: VersionTLS12\n' >> /var/lib/kubelet/config.yaml"
podman exec $WORKER systemctl restart kubelet
kubectl get --raw "/api/v1/nodes/$WORKER/proxy/configz" | python3 -m json.tool | grep -e tlsMinVersion -e readOnlyPort
```

The `configz` output shows `"tlsMinVersion": "VersionTLS12"`. The field `readOnlyPort` is absent, because the kubelet omits a zero value from the output, and absent means the port is closed. If the request returns an error right after the restart, wait a few seconds and run it again.

## Certificates and rotation

Two more fields matter for certificates. `rotateCertificates: true` makes the kubelet request a new client certificate from the API server before the old one expires. Without it, the client certificate expires after its validity period, usually one year, and the node stops working. `serverTLSBootstrap: true` makes the kubelet request its serving certificate through the certificate signing request (CSR) API instead of using a self-signed one. These requests need approval, either by an administrator or by a controller you install, and until a request is approved the kubelet cannot serve a certificate that clients trust. This is why the playground does not turn `serverTLSBootstrap` on. The benchmark asks for both settings, and a real cluster that enables the second one must also have a plan for approving the requests.

You have closed the unauthenticated listener and set a minimum TLS version. The kubelet has further checks on kernel behaviour, timeouts and files. The next part covers them.

## Common pitfalls

> [!WARNING]
> - **Closing only port `10250` protection.** Port `10255` needs no credentials. Set `readOnlyPort: 0`.
> - **Writing the key twice.** A duplicate key stops the kubelet. Remove the old line first.
> - **Enabling `serverTLSBootstrap` without approving requests.** The pending requests leave the kubelet without a trusted serving certificate.
> - **Using a very narrow `tlsCipherSuites` list.** Clients that support none of the ciphers lose access. Test the API server and your monitoring after the change.
