# Summary

The kubelet takes its settings from three kinds of source: the configuration file `/var/lib/kubelet/config.yaml`, command-line flags and compiled defaults. A flag overrides the same field in the file. The `configz` endpoint, reached through the API server, shows the merged result. So a review reads `configz` and does not rely on the file alone.

The kubelet does not check its file before it starts. A safe edit therefore has a backup, one change at a time, a check of the file, a restart and a check of the effective value. A duplicate key or a typo stops the kubelet.

Authentication decides who a caller is, and authorization decides what the caller may do. The benchmark requires anonymous authentication to be off and the authorization mode to be `Webhook`, so that the API server and role-based access control (RBAC) decide each request. The answer code shows which setting stopped a request:

- without credentials and with anonymous authentication off, the kubelet answers `401`;
- with anonymous access on and `Webhook` authorization, it answers `403`;
- with both settings weak, it answers `200` and lists the pods of the node.

The `x509` client certificate authority (CA) must stay in place, because the API server connects to the kubelet with a certificate.

The read-only port `10255` serves plain HTTP with no authentication, and `readOnlyPort: 0` closes it. The Transport Layer Security (TLS) options set the lowest protocol version and the allowed ciphers. `rotateCertificates` renews the client certificate before it expires. `serverTLSBootstrap` needs a plan for approving certificate requests.

`protectKernelDefaults` makes the kubelet refuse to start when kernel parameters differ from the values it expects. So the expected values go into a file in `/etc/sysctl.d` before the field is turned on. An explicit `streamingConnectionIdleTimeout` closes idle streams. The kubelet configuration file and kubeconfig need mode `600` and the owner `root`.

CoreDNS provides cluster DNS (Domain Name System) as the Deployment `coredns` in `kube-system`, behind the Service `kube-dns`. The benchmark editions known here have no numbered checks for it, so its review is manual. A good result has a minimal security context, a Corefile whose plugins are understood, and RBAC that keeps the ConfigMap and the Deployment away from ordinary workloads.

The remediation loop is the same for every component: audit, back up, change one setting, restart, audit again and compare. A file edit is not a result. The result is the effective value on the running process and a working node. A tool such as `kube-bench` helps with the audit. It reports manual checks, such as the read-only port, as warnings, so a review reads the warnings as well as the failures.

Key facts to remember:

- Flags override the kubelet file, and `configz` shows the effective values.
- Anonymous authentication off and `Webhook` authorization are both required.
- `readOnlyPort: 0` closes the unauthenticated HTTP port.
- Save the kernel parameters in `/etc/sysctl.d` before you turn on `protectKernelDefaults`.
- Prove each fix with a request or a value from the running process.

<!-- astrona:playground:destroy -->
