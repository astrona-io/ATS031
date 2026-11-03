---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Other Kubelet Checks

Besides authentication and ports, the benchmark checks a handful of kubelet settings about kernel behaviour, firewall rules, event recording and idle connections, and it checks the permissions of the kubelet files. Each of these checks has a different risk when you apply it. Some are safe, one can stop the kubelet on the wrong machine, and some depend on how you run the node. This part explains each one and applies the safe ones.

## protectKernelDefaults

The field `protectKernelDefaults: true` makes the kubelet compare a list of kernel parameters with the values it expects, such as `vm.overcommit_memory` and `kernel.panic`. If a value differs, the kubelet fails to start instead of changing the kernel. The benchmark asks for the setting because it prevents a node from running with unexpected kernel behaviour.

Do not turn this on in the `kind` playground. A kind node is a container that shares the kernel of the host, so you cannot set kernel parameters per node, and a kubelet that expects other values refuses to start. The node would go `NotReady`. On a dedicated machine, set the kernel parameters first with a file in `/etc/sysctl.d`, and then enable the field. In a kind cluster a reviewer records this finding as not applicable to the environment, with the reason.

## makeIPTablesUtilChains, eventRecordQPS and the idle timeout

`makeIPTablesUtilChains: true` lets the kubelet create the iptables chains it needs for its own rules. The default is `true`, and the benchmark requires that it is not `false`. `eventRecordQPS` limits how many events per second the kubelet records. The benchmark accepts `0`, which means no limit, or a value that still records enough events for investigation. The default is higher than old guides state, so check the effective value in `configz` and judge it against your own needs.

`streamingConnectionIdleTimeout` is the time after which the kubelet closes an idle streaming connection, such as the one of `kubectl exec` or `kubectl logs -f`. The benchmark requires that it is not set to `0`, because a forgotten session then stays open without limit. A kubeadm file may contain the value `0s`, and the kubelet treats that as unset and applies its default. Because the intent of a file with `0s` is unclear to a reader and to a tool, a reviewer sets an explicit value such as `5m`.

## Look at the effective values

Print these fields from `configz`. The `grep` keeps only the lines you need:

<!-- astrona:playground:renew -->

```sh
WORKER=astro-ats-031-playground-020-05-worker
kubectl get --raw "/api/v1/nodes/$WORKER/proxy/configz" | python3 -m json.tool | grep -e protectKernelDefaults -e makeIPTablesUtilChains -e eventRecordQPS -e streamingConnectionIdleTimeout -e rotateCertificates
```

A field that equals its default can be missing from the output, as `readOnlyPort` is. Read each line next to the benchmark text. If a field you expect is not there, look in `config.yaml` to see whether the file sets it.

## Apply the safe settings

Set the idle timeout and certificate rotation with the remove-and-append routine, and restart the kubelet. Both settings are safe on `kind`:

```sh
podman exec $WORKER cp /var/lib/kubelet/config.yaml /root/kubelet-config.yaml.bak
podman exec $WORKER sed -i -e '/^streamingConnectionIdleTimeout:/d' -e '/^rotateCertificates:/d' /var/lib/kubelet/config.yaml
podman exec $WORKER sh -c "printf '\nstreamingConnectionIdleTimeout: 5m\nrotateCertificates: true\n' >> /var/lib/kubelet/config.yaml"
podman exec $WORKER systemctl restart kubelet
```

After about ten seconds, read the effective values again with the previous command. `streamingConnectionIdleTimeout` shows `5m0s` and `rotateCertificates` shows `true`.

## Kubelet file permissions

The benchmark section on worker nodes also checks files. The kubelet service file should have mode `600` or stricter. The kubelet kubeconfig, `/etc/kubernetes/kubelet.conf`, and the configuration file, `/var/lib/kubelet/config.yaml`, should have mode `600` or stricter and belong to `root:root`. The client CA file named in `x509.clientCAFile` should have mode `600` or stricter. These recommendations differ in the exact mode between editions, so read the audit text of your edition. The kubelet runs as `root` and reads the files as `root`, so a stricter mode does not affect it.

Print the current state, fix the two files and print again:

```sh
podman exec $WORKER stat -c '%a %U:%G %n' /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf /etc/kubernetes/pki/ca.crt
podman exec $WORKER chmod 600 /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
podman exec $WORKER stat -c '%a %U:%G %n' /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
```

In the playground, the two files start with mode `644`. The second `stat` shows `600`. The CA certificate `ca.crt` is a public certificate, and the benchmark accepts mode `644` for certificate files, so do not change it to match a different rule.

You have a list of the remaining kubelet checks and know which ones are safe to apply. The kubelet is only one of the components with a security-relevant configuration. Cluster DNS is the next one.

## Common pitfalls

> [!WARNING]
> - **Enabling `protectKernelDefaults` on `kind`.** The kubelet refuses to start when the shared kernel differs from its expectations.
> - **Copying a number from a guide.** Read the audit text of the benchmark edition you use and check the effective value.
> - **Using `chmod -R` on `/etc/kubernetes`.** Certificates and manifests have different required modes. Change named files.
> - **Counting a `0s` value as a secure setting.** An unclear value is a finding for review. Set an explicit value.
