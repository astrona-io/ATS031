---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow DNS And One Application Dependency Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-01-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-01-02" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

An egress policy controls the traffic that leaves a pod. Once a policy selects the `scanner` pod for `Egress`, the pod may only open connections that some egress rule allows. A pod that uses names also needs DNS, so the policy needs two rules: one to CoreDNS, the cluster DNS server, and one to the `archive` pods.

The DNS rule uses one peer entry with both a `namespaceSelector` and a `podSelector`. Together they mean "pods with the label `k8s-app: kube-dns` in the namespace `kube-system`". DNS uses UDP port 53 for most queries and TCP port 53 for large answers, so the rule allows both. The archive rule uses TCP port 8080, the container port: the network plugin checks the pod address and pod port after the Service has translated the request, not the Service port 80.

Save this as `networkpolicy-scanner-egress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: scanner-egress
  namespace: starfleet-031-010-01-02
spec:
  podSelector:
    matchLabels:
      app: scanner
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
  - to:
    - podSelector:
        matchLabels:
          app: archive
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-scanner-egress.yaml
```

Then check the result. The test client prints `open` with the reply, `blocked` when the connection times out, and `resolved` or `unresolved` for a DNS lookup:

```sh
kubectl -n starfleet-031-010-01-02 exec scanner -- python /app/client.py dns archive.starfleet-031-010-01-02.svc.cluster.local
ARCHIVE_SERVICE_IP=$(kubectl -n starfleet-031-010-01-02 get service archive -o jsonpath='{.spec.clusterIP}')
DECOY_IP=$(kubectl -n starfleet-031-010-01-02 get pod decoy -o jsonpath='{.status.podIP}')
kubectl -n starfleet-031-010-01-02 exec scanner -- python /app/client.py tcp "$ARCHIVE_SERVICE_IP" 80
kubectl -n starfleet-031-010-01-02 exec scanner -- python /app/client.py tcp "$DECOY_IP" 8080
```

The lookup must print `resolved` and the Service address. The request to the archive must print `open` and the request to the decoy must print `blocked`.

The lookup succeeds because the DNS rule matches the CoreDNS pods. The request to the Service on port 80 succeeds because kube-proxy translates it to an `archive` pod on port 8080, which the second rule allows. The request to the `decoy` pod times out, because no rule allows it, while the `idler` pod can still reach the `decoy`.

When you are done, remove the lab with `astrona destroy ats-031-lab-010-01-02`.

## Common pitfalls

> [!WARNING]
> If you write port 80 in the archive rule, the Service request fails: policies see the pod port after the Service translation, not the Service port.
>
> Two separate peer entries, one with the `namespaceSelector` and one with the `podSelector`, are joined with OR. That allows every pod in `kube-system`, not only CoreDNS.
