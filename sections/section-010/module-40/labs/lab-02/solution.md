---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow Only DNS Egress Under A Baseline Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-04-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-04-02" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

Under a default-deny baseline, a pod cannot even resolve names. A DNS egress rule allows UDP and TCP port 53 to the CoreDNS pods, which carry the label `k8s-app: kube-dns` in `kube-system`. Selecting the CoreDNS pods, not a wide address range, keeps the rule narrow.

Save this as `networkpolicy-navigator-dns.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: navigator-dns
  namespace: starfleet-031-010-04-02
spec:
  podSelector:
    matchLabels:
      app: navigator
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
```

Apply it:

```sh
kubectl apply -f networkpolicy-navigator-dns.yaml
```

Then check the result. The test client prints `resolved` with the address, or `unresolved` when the lookup gets no answer:

```sh
kubectl -n starfleet-031-010-04-02 exec navigator -- python /app/client.py dns kubernetes.default.svc.cluster.local
kubectl -n starfleet-031-010-04-02 exec cargo -- python /app/client.py dns kubernetes.default.svc.cluster.local
```

The first command must print `resolved` and the second `unresolved`.

The `navigator` pod resolves the name, because its rule allows port 53 to CoreDNS. The `cargo` pod still prints `unresolved`, because the policy selects only `navigator`. The `navigator` pod also cannot reach CoreDNS on its metrics port 9153, because the rule allows only port 53.

When you are done, remove the lab with `astrona destroy ats-031-lab-010-04-02`.

## Common pitfalls

> [!WARNING]
> Allow both UDP and TCP port 53. Large DNS answers switch to TCP, and a UDP-only rule fails in ways that are hard to see.
>
> A rule `to` CoreDNS without `ports` allows every port on those pods. Always list the ports.
