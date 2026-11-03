---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Summary

The kubelet takes its settings from the configuration file `/var/lib/kubelet/config.yaml`, from command-line flags and from compiled defaults. A flag overrides the same field in the file. The `configz` endpoint, reached through the API server, shows the merged result, so a review reads it and does not rely on the file alone. The kubelet does not check its file before it starts, so a safe edit has a backup, one change at a time, a check of the file, a restart and a check of the effective value. A duplicate key or a typo stops the kubelet.

Authentication decides who a caller is, and authorization decides what the caller may do. The benchmark requires anonymous authentication to be off and the authorization mode to be `Webhook`, so that the API server and RBAC decide each request. Without credentials the kubelet answers `401`. With anonymous access on and `Webhook` authorization it answers `403`. With both weak it answers `200` and lists the pods of the node. The `x509` client CA must stay in place, because the API server connects to the kubelet with a certificate.

The read-only port `10255` serves plain HTTP with no authentication, and `readOnlyPort: 0` closes it. The TLS options set the lowest protocol version and the allowed ciphers, and `rotateCertificates` renews the client certificate before it expires. `serverTLSBootstrap` needs a plan for approving certificate requests. `protectKernelDefaults` makes the kubelet refuse to start when kernel parameters differ from its expectations, so it is not safe on a `kind` node that shares the kernel of the host. An explicit `streamingConnectionIdleTimeout` closes idle streams, and the kubelet configuration file and kubeconfig need mode `600` and owner `root`.

CoreDNS provides cluster DNS as the Deployment `coredns` in `kube-system`, behind the Service `kube-dns`. The benchmark editions known here have no numbered checks for it, so its review is manual: a minimal security context, a Corefile whose plugins are understood, and RBAC that keeps the ConfigMap and the Deployment away from ordinary workloads.

The remediation loop is the same for every component: audit, back up, change one setting, restart, audit again and compare. A file edit is not a result. The result is the effective value on the running process and a working node. A tool such as `kube-bench` helps with the audit, and on a `kind` node some of its findings come from the container layout and are recorded as not applicable.

Key facts to remember:

- Flags override the kubelet file, and `configz` shows the effective values.
- Anonymous authentication off and `Webhook` authorization are both required.
- `readOnlyPort: 0` closes the unauthenticated HTTP port.
- Do not enable `protectKernelDefaults` on `kind`.
- Prove each fix with a request or a value from the running process.

<!-- astrona:playground:destroy -->
