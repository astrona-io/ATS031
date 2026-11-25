---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Repair A Two-Entry Peer Rule Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-03-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-03-02" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

The policy lists the `namespaceSelector` and the `podSelector` as two peer entries, so they are joined with OR. It admits every pod in `starfleet-031-010-03-02` and every pod with `app: sampler` in `dock-031-010-03-02`, the policy's own namespace. That is why the `idler` pod and the local `sampler` get in.

Look at the current rule:

```sh
kubectl -n dock-031-010-03-02 get networkpolicy assay-from-starfleet -o yaml
```

The `from` list has two items, each starting with `- `. Merge them into one item.

Save this as `networkpolicy-assay-from-starfleet.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: assay-from-starfleet
  namespace: dock-031-010-03-02
spec:
  podSelector:
    matchLabels:
      app: assay
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: starfleet-031-010-03-02
      podSelector:
        matchLabels:
          app: sampler
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-assay-from-starfleet.yaml
```

Then check the result. The test client prints `open` with the reply, or `blocked` when the connection times out:

```sh
ASSAY_IP=$(kubectl -n dock-031-010-03-02 get pod assay -o jsonpath='{.status.podIP}')
kubectl -n starfleet-031-010-03-02 exec sampler -- python /app/client.py tcp "$ASSAY_IP" 8080
kubectl -n starfleet-031-010-03-02 exec idler -- python /app/client.py tcp "$ASSAY_IP" 8080
kubectl -n dock-031-010-03-02 exec sampler -- python /app/client.py tcp "$ASSAY_IP" 8080
```

The first command must print `open`. The other two must print `blocked`.

Only the `sampler` pod in `starfleet-031-010-03-02` gets a reply now, because one peer entry requires both the namespace and the pod label. The `idler` pod fails the pod label, and the other `sampler` pods fail the namespace.

When you are done, remove the lab with `astrona destroy ats-031-lab-010-03-02`.

## Common pitfalls

> [!WARNING]
> `kubectl apply` replaces the `from` list with the one in your file. Check the result with `-o yaml` and count the peer entries.
>
> A two-entry rule is a common review finding: it looks narrow but admits every pod of the selected namespace.
