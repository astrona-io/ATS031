# Other Kubelet Checks

Besides authentication and ports, the benchmark checks a handful of kubelet settings. They cover kernel behaviour, firewall rules, event recording and idle connections. The benchmark also checks the permissions of the kubelet files.

Each of these checks carries a different risk when you apply it. Some are safe. One stops the kubelet if the kernel is not prepared. Others depend on how you run the node. This page explains each check and applies them in a safe order.

## protectKernelDefaults

The field `protectKernelDefaults: true` makes the kubelet compare a list of kernel parameters with the values it expects, such as `vm.overcommit_memory` and `kernel.panic`. If a value differs, the kubelet fails to start instead of changing the kernel. The benchmark asks for this setting because it stops a node from running with unexpected kernel behaviour.

The kubelet checks these kernel parameters:

- `vm.overcommit_memory` must be `1`;
- `vm.panic_on_oom` must be `0`;
- `kernel.panic` must be `10`;
- `kernel.panic_on_oops` must be `1`.

Without `protectKernelDefaults`, the kubelet sets these values itself when it starts. That is why they can look correct on a running node even when no file sets them. After a reboot, the kernel starts with its own defaults. A kubelet with `protectKernelDefaults: true` then refuses to start.

So the safe order has three steps. First write the values to a file in `/etc/sysctl.d`, then load them, and only then turn on the field.

![Diagram: in the unsafe order the values are set only by the kubelet, protectKernelDefaults is turned on, the node reboots and the kubelet fails with invalid kernel flag; in the safe order the values are written to 90-kubelet.conf and loaded with sysctl -p before protectKernelDefaults is turned on, so the kubelet starts after a reboot](images/protect-kernel-defaults-order.svg)

The drawing compares the two orders: only the order that saves the values in a file first survives a reboot.

## makeIPTablesUtilChains, eventRecordQPS and the idle timeout

Three more fields are less risky to change, but each needs a careful reading:

- `makeIPTablesUtilChains: true` lets the kubelet create the iptables chains it needs for its own rules. iptables is the Linux packet filter. The default is `true`, and the benchmark requires that it is not `false`.
- `eventRecordQPS` limits how many events per second the kubelet records. The benchmark accepts `0`, which means no limit, or a value that still records enough events for an investigation. The default is higher than old guides state, so check the effective value in `configz` and judge it against your own needs.
- `streamingConnectionIdleTimeout` is the time after which the kubelet closes an idle streaming connection, such as the one of `kubectl exec` or `kubectl logs -f`. The benchmark requires that it is not set to `0`, because a forgotten session then stays open without limit.

The idle timeout has one unclear case. A kubeadm file may contain the value `0s`, and the kubelet treats that as unset and applies its default. The intent of a file with `0s` is unclear to a reader and to a tool, so a reviewer sets an explicit value such as `5m`.

## Look at the effective values

Before you change anything, see what the kubelet runs with now. Open a shell on the node and print these fields from `configz`. The `grep` keeps only the lines you need:

<!-- astrona:playground:renew -->

```sh
astrona ssh astro-ats-031-playground-020-05
NODE=astro-ats-031-playground-020-05
kubectl get --raw "/api/v1/nodes/$NODE/proxy/configz" | python3 -m json.tool | grep -e protectKernelDefaults -e makeIPTablesUtilChains -e eventRecordQPS -e streamingConnectionIdleTimeout -e rotateCertificates
```

In the starting state of the playground the output is:

```text
        "eventRecordQPS": 50,
        "streamingConnectionIdleTimeout": "4h0m0s",
        "makeIPTablesUtilChains": true,
```

Two fields are missing. The kubelet leaves out a field whose value is `false`, so `protectKernelDefaults` and `rotateCertificates` do not appear. The file sets `streamingConnectionIdleTimeout: 0s`, but the effective value is `4h0m0s`, the default. This is the unclear case from above.

Read each line next to the benchmark text. If a field you expect is not there, look in `config.yaml` to see whether the file sets it.

## Apply the settings

You change the kubelet in two steps: first the kernel, then the kubelet file. Start by preparing the kernel for `protectKernelDefaults`. Print the four parameters that the kubelet checks:

```sh
sysctl vm.overcommit_memory vm.panic_on_oom kernel.panic kernel.panic_on_oops
```

On this node they already have the expected values, because the kubelet set them when it started:

```text
vm.overcommit_memory = 1
vm.panic_on_oom = 0
kernel.panic = 10
kernel.panic_on_oops = 1
```

No file in `/etc/sysctl.d` sets them yet, so they would not survive a reboot. Write them to a file and load the file with `sysctl -p`. Both commands print the four values again:

```sh
printf 'vm.overcommit_memory = 1\nvm.panic_on_oom = 0\nkernel.panic = 10\nkernel.panic_on_oops = 1\n' | sudo tee /etc/sysctl.d/90-kubelet.conf
sudo sysctl -p /etc/sysctl.d/90-kubelet.conf
```

Now the kernel is ready. Set the idle timeout, certificate rotation and kernel protection with the remove-and-append routine, and restart the kubelet:

```sh
sudo cp /var/lib/kubelet/config.yaml /root/kubelet-config.yaml.bak
sudo sed -i -e '/^streamingConnectionIdleTimeout:/d' -e '/^rotateCertificates:/d' -e '/^protectKernelDefaults:/d' /var/lib/kubelet/config.yaml
printf '\nstreamingConnectionIdleTimeout: 5m\nrotateCertificates: true\nprotectKernelDefaults: true\n' | sudo tee -a /var/lib/kubelet/config.yaml >/dev/null
sudo systemctl restart kubelet
```

After about ten seconds, run the `configz` command from above again. The output now shows the new values:

```text
        "rotateCertificates": true,
        "eventRecordQPS": 50,
        "streamingConnectionIdleTimeout": "5m0s",
        "protectKernelDefaults": true,
        "makeIPTablesUtilChains": true,
```

Run `kubectl get node $NODE` and confirm that the node is still `Ready`.

If one kernel parameter differs, the kubelet does not start. In a test on this node with `kernel.panic` set to `0`, the kubelet stayed in the state `activating`. Its log (`sudo journalctl -u kubelet`) showed this line:

```text
E1118 08:47:37.482173    3808 kubelet.go:1750] "Failed to start ContainerManager" err="invalid kernel flag: kernel/panic, expected value: 10, actual value: 0"
```

The log line names the parameter, the expected value and the actual value, so you know exactly which value to fix.

## Kubelet file permissions

The settings are done, but the benchmark section on worker nodes also checks files. A file mode such as `600` means that only the owner may read and write the file. The checks ask for these modes:

- The kubelet service file should have mode `600` or stricter.
- The kubelet kubeconfig, `/etc/kubernetes/kubelet.conf`, should have mode `600` or stricter and belong to `root:root`.
- The configuration file, `/var/lib/kubelet/config.yaml`, should have mode `600` or stricter and belong to `root:root`.
- The client CA file named in `x509.clientCAFile` should have mode `600` or stricter.

The exact modes differ between editions of the benchmark, so read the audit text of your edition. The kubelet runs as `root` and reads the files as `root`, so a stricter mode does not affect it.

Print the current state, fix the two files and print again:

```sh
sudo stat -c '%a %U:%G %n' /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf /etc/kubernetes/pki/ca.crt
sudo chmod 600 /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
sudo stat -c '%a %U:%G %n' /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
```

The output is:

```text
644 root:root /var/lib/kubelet/config.yaml
644 root:root /etc/kubernetes/kubelet.conf
644 root:root /etc/kubernetes/pki/ca.crt
600 root:root /var/lib/kubelet/config.yaml
600 root:root /etc/kubernetes/kubelet.conf
```

In the playground, the two kubelet files start with mode `644`, and the second `stat` shows `600`. The certificate authority (CA) file `ca.crt` also shows `644`. The benchmark asks for `600` or stricter on this file in check 4.1.7, which is a manual check. kube-bench, the tool that runs the benchmark checks, reports it as `[WARN]`, not `[FAIL]`. The file holds only a public certificate, so the risk is small, but a review still records it.

You now know the remaining kubelet checks and the safe order to apply them in. The kubelet is only one of the components with a security-relevant configuration, and the question still open is how to review cluster DNS (Domain Name System), the service that every pod uses to find Services by name.

## Common pitfalls

> [!WARNING]
> - **Turning on `protectKernelDefaults` before the kernel parameters are in `/etc/sysctl.d`.** The values can look right on a running node, because the kubelet set them. After a reboot, the kubelet refuses to start.
> - **Copying a number from a guide.** Read the audit text of the benchmark edition you use, and check the effective value.
> - **Using `chmod -R` on `/etc/kubernetes`.** Certificates and manifests have different required modes. Change only the named files.
> - **Counting a `0s` value as a secure setting.** An unclear value is a finding for review. Set an explicit value.
