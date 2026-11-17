---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow One Pod From Another Namespace Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-03-01" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

A peer entry in `from` can hold a `namespaceSelector` and a `podSelector` together. In one entry they are joined with AND: the sender must be in a selected namespace and carry the selected pod label. This is the way to admit one pod from one other namespace.

Save this as `networkpolicy-registry-from-outpost-courier.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: registry-from-outpost-courier
  namespace: starfleet-031-010-03-01
spec:
  podSelector:
    matchLabels:
      app: registry
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: outpost-031-010-03-01
      podSelector:
        matchLabels:
          app: courier
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-registry-from-outpost-courier.yaml
```

Then check the result. The test client prints `open` with the reply, or `blocked` when the connection times out:

```sh
REGISTRY_IP=$(kubectl -n starfleet-031-010-03-01 get pod registry -o jsonpath='{.status.podIP}')
kubectl -n outpost-031-010-03-01 exec courier -- python /app/client.py tcp "$REGISTRY_IP" 8080
kubectl -n dock-031-010-03-01 exec courier -- python /app/client.py tcp "$REGISTRY_IP" 8080
kubectl -n starfleet-031-010-03-01 exec courier -- python /app/client.py tcp "$REGISTRY_IP" 8080
```

The first command must print `open`. The other two must print `blocked`.

Only the `courier` pod in `outpost-031-010-03-01` gets a reply. The `courier` pods in `dock-031-010-03-01` and `starfleet-031-010-03-01` carry the same label, but their namespaces do not match the `namespaceSelector`. A `podSelector` alone would have admitted only the `courier` in the policy's own namespace.

When you are done, remove the lab with `astrona destroy ats-031-lab-010-03-01`.

## Common pitfalls

> [!WARNING]
> Indentation decides the meaning. A `- ` in front of `podSelector` starts a second peer entry, and the two entries are joined with OR.
>
> Select the namespace by `kubernetes.io/metadata.name`. The API server sets this label on every namespace, so it always exists.
