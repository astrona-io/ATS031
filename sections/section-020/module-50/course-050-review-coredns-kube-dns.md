# Review CoreDNS (kube-dns)

Every pod resolves Service names through the cluster DNS (Domain Name System) service. If an attacker changes its configuration, the attacker can send pods to the wrong address. A flaw in the DNS server also affects every namespace at once.

The exam objective names `kubedns`, the original cluster DNS component. Current clusters, including clusters built with kubeadm, run CoreDNS instead. The Service in front of CoreDNS keeps the name `kube-dns`. This page reviews the CoreDNS Deployment, its Corefile and who may change them.

## What the benchmark covers

You might expect a list of numbered DNS checks, but there is none. The Center for Internet Security (CIS) Kubernetes Benchmark editions known to this course contain no section with checks for the CoreDNS Deployment itself. So the review of cluster DNS is a manual review that applies general rules:

- the container runs without extra privileges;
- the configuration is read-only for most users;
- the plugins in the Corefile do what you expect.

Treat the items on this page as a reviewer's list, not as numbered checks.

![Diagram: the shuttle pod sends a DNS query to the kube-dns Service, which passes it to the coredns pods in kube-system; the kubernetes plugin answers cluster.local names and the forward plugin sends other names to the servers in /etc/resolv.conf; the pods reload the Corefile from the ConfigMap coredns, and RBAC decides who may change it](images/coredns-review.svg)

The drawing shows the path of a DNS query and the three things to review: the `coredns` pods, the ConfigMap that holds the Corefile, and the RBAC rules that decide who may change it.

## The Deployment

Start with the pods themselves. CoreDNS runs as the Deployment `coredns` in the `kube-system` namespace. The pod needs to listen on port `53`, which is a privileged port. So it needs the Linux capability `NET_BIND_SERVICE` and nothing else. A capability is one piece of the `root` user's power that a process can get on its own.

The kubeadm manifest drops all other capabilities, forbids privilege escalation and mounts the root filesystem read-only. Print the security context of the container and the service account:

<!-- astrona:playground:renew -->

```sh
kubectl -n kube-system get deployment coredns -o jsonpath='{.spec.template.spec.containers[0].securityContext}{"\n"}{.spec.template.spec.serviceAccountName}{"\n"}'
```

Look for these values in the output:

- `allowPrivilegeEscalation` set to `false`;
- the capability list with `drop` set to `ALL` and `add` set to `NET_BIND_SERVICE`;
- `readOnlyRootFilesystem` set to `true`.

The values can differ between versions of the manifest, so judge what you see against the rule: no privilege that DNS does not need. The service account is `coredns`. Its ClusterRole `system:coredns` lets it list Services, Endpoints, Namespaces and EndpointSlices. That is what the `kubernetes` plugin needs to answer queries.

## The Corefile

The pods are only half of the review; the other half is what they are told to do. CoreDNS reads its configuration from a file called the Corefile. Kubernetes stores it in the ConfigMap `coredns` in `kube-system`. Print it:

```sh
kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}'
```

The default Corefile has a server block for the root zone `.` on port `53`, with a list of plugins. These are the plugins with a security meaning:

- `kubernetes cluster.local in-addr.arpa ip6.arpa` answers names inside the cluster. Its option `pods insecure` returns an address for a pod name built from an IP address, without checking that the pod exists. The value `verified` checks the pod, and `disabled` turns the pod records off. `insecure` exists for compatibility with the older kube-dns.
- `forward . /etc/resolv.conf` sends names outside the cluster to the DNS servers of the node. Every server in that file receives the queries of all pods, so review the node's resolver settings.
- `cache 30` keeps answers for 30 seconds. `loop` stops the server when it detects a forwarding loop. `errors`, `health`, `ready` and `reload` cover logging, probes and automatic reload. `prometheus :9153` opens a metrics port.

The `reload` plugin means that the running pods apply a change to the ConfigMap after a short delay, without a restart. This is also the reason to protect the ConfigMap: anyone who can update it changes the DNS answers of the whole cluster.

## Who may change it

That leads to the last question: who can write to the ConfigMap or the Deployment? Kubernetes role-based access control (RBAC) decides this. The `auth can-i` command asks the API server whether a user or service account may do an action. Here it asks for the default service account of `starfleet`, which the `shuttle` pod uses:

```sh
kubectl auth can-i update configmap/coredns -n kube-system --as=system:serviceaccount:starfleet:default
```

The answer is `no`. A role that allows `update` on ConfigMaps in `kube-system`, or a wide `edit` binding there, would allow a change. Review such roles when you review DNS. A compromised pod that holds such a role could redirect names such as `probe.starfleet.svc.cluster.local`.

## Test resolution

After the review, confirm that DNS still works for a normal workload. From the `shuttle` pod, resolve the name of the `probe` Service. The `kubernetes` plugin answers this name from the cluster:

```sh
kubectl -n starfleet exec shuttle -- nslookup probe.starfleet.svc.cluster.local
```

The answer shows the cluster IP address of the `probe` Service. It names the cluster DNS Service address as the DNS server. A name outside the cluster goes through the `forward` plugin and depends on the network of your host. So a failure there is not a security finding on its own.

You now have a manual review list for cluster DNS: a minimal security context, a configuration that only the cluster operators can change, and a Corefile whose plugins you can explain. The question still open is how to join all these fixes into one repeatable loop with proof of each result.

## Common pitfalls

> [!WARNING]
> - **Looking for numbered DNS checks.** The benchmark editions known here have none for CoreDNS. Record the review as manual.
> - **Treating `pods insecure` as a finding without context.** It is the default for compatibility. Judge it against your own needs.
> - **Forgetting RBAC.** A broad role on ConfigMaps in `kube-system` can change the DNS answers of the cluster.
> - **Editing the Corefile without a backup.** The `reload` plugin applies a syntax error to every pod. Save the old ConfigMap first.
