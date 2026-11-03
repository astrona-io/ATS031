---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Review CoreDNS (kube-dns)

Every pod resolves Service names through the cluster DNS (Domain Name System) service. If an attacker changes its configuration, the attacker can send pods to the wrong address, and a flaw in the DNS server affects every namespace. The exam objective names `kubedns`, the original cluster DNS component. Current clusters, including kubeadm and `kind`, run CoreDNS instead, and the Service in front of it keeps the name `kube-dns`. This part reviews the CoreDNS Deployment, its Corefile and who may change them.

## What the benchmark covers

The CIS Kubernetes Benchmark editions known to this course contain no section with checks for the CoreDNS Deployment itself. The review of cluster DNS is therefore a manual review that applies general rules: the container runs without extra privileges, the configuration is read-only for most users, and the plugins in the Corefile do what you expect. Treat the items below as a reviewer's list, not as numbered checks.

## The Deployment

CoreDNS runs as the Deployment `coredns` in the `kube-system` namespace. The pod needs to listen on port `53`, which is a privileged port, so it needs the Linux capability `NET_BIND_SERVICE` and nothing else. The kubeadm manifest drops all other capabilities, forbids privilege escalation and mounts the root filesystem read-only. Print the security context of the container and the service account:

<!-- astrona:playground:renew -->

```sh
kubectl -n kube-system get deployment coredns -o jsonpath='{.spec.template.spec.containers[0].securityContext}{"\n"}{.spec.template.spec.serviceAccountName}{"\n"}'
```

Look for `allowPrivilegeEscalation` set to `false`, the capability list with `drop` set to `ALL` and `add` set to `NET_BIND_SERVICE`, and `readOnlyRootFilesystem` set to `true`. The values can differ between versions of the manifest, so judge what you see against the rule: no privilege that DNS does not need. The service account is `coredns`. Its ClusterRole `system:coredns` lets it list Services, Endpoints, Namespaces and EndpointSlices, which is what the `kubernetes` plugin needs to answer queries.

## The Corefile

CoreDNS reads its configuration from a file called the Corefile, which Kubernetes stores in the ConfigMap `coredns` in `kube-system`. Print it:

```sh
kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}'
```

The default Corefile has a server block for the root zone `.` on port `53` with a list of plugins. Read the ones with security meaning.

- `kubernetes cluster.local in-addr.arpa ip6.arpa` answers names inside the cluster. Its option `pods insecure` returns an address for a pod name built from an IP address without checking that the pod exists. The value `verified` checks the pod, and `disabled` turns the pod records off. `insecure` exists for compatibility with the older kube-dns.
- `forward . /etc/resolv.conf` sends names outside the cluster to the DNS servers of the node. Any server in that file receives the queries of all pods, so review the node's resolver settings.
- `cache 30` keeps answers for 30 seconds. `loop` stops the server when it detects a forwarding loop. `errors`, `health`, `ready` and `reload` cover logging, probes and automatic reload. `prometheus :9153` opens a metrics port.

The `reload` plugin means a change to the ConfigMap is applied by the running pods without a restart, after a short delay. This is also the reason to protect the ConfigMap: anyone who can update it changes the DNS answers of the whole cluster.

## Who may change it

Kubernetes RBAC controls who can edit the ConfigMap or the Deployment. The `auth can-i` command asks the API server whether a user or service account may do an action. This asks it for the default service account of `starfleet`, which the `shuttle` pod uses:

```sh
kubectl auth can-i update configmap/coredns -n kube-system --as=system:serviceaccount:starfleet:default
```

The answer is `no`. A role that allows `update` on ConfigMaps in `kube-system`, or a wide `edit` binding there, would allow a change. Review such roles when you review DNS. A pod that is compromised and holds such a role could redirect names such as `probe.starfleet.svc.cluster.local`.

## Test resolution

From the `shuttle` pod, resolve the name of the `probe` Service. The `kubernetes` plugin answers this name from the cluster:

```sh
kubectl -n starfleet exec shuttle -- nslookup probe.starfleet.svc.cluster.local
```

The answer shows the cluster IP of the `probe` Service and names the DNS server as the cluster DNS Service address. A name outside the cluster goes through the `forward` plugin and depends on the network of your host, so a failure there is not a security finding on its own.

You have a manual review list for cluster DNS: a minimal security context, a read-only configuration for everyone except the operators of the cluster, and a Corefile whose plugins you can explain. The last part joins everything into one loop.

## Common pitfalls

> [!WARNING]
> - **Looking for numbered DNS checks.** The benchmark has none for CoreDNS in the editions known here. Record the review as manual.
> - **Treating `pods insecure` as a finding without context.** It is the default for compatibility. Judge it against your own needs.
> - **Forgetting RBAC.** A broad role on ConfigMaps in `kube-system` can change the DNS answers of the cluster.
> - **Editing the Corefile without a backup.** The `reload` plugin applies a syntax error to every pod. Save the old ConfigMap first.
