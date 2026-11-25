---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Admit A Group Of Namespaces By Label Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-03-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-03-03" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

A `namespaceSelector` with a label you choose admits a group of namespaces. Any namespace that carries the label later joins the group without a change to the policy. Label the two namespaces first, then write the policy.

Add the label to the two namespaces:

```sh
kubectl label namespace survey-031-010-03-03 division=science
kubectl label namespace salvage-031-010-03-03 division=science
```

Save this as `networkpolicy-archive-from-science.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: archive-from-science
  namespace: starfleet-031-010-03-03
spec:
  podSelector:
    matchLabels:
      app: archive
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          division: science
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-archive-from-science.yaml
```

Then check the result. The test client prints `open` with the reply, or `blocked` when the connection times out:

```sh
ARCHIVE_IP=$(kubectl -n starfleet-031-010-03-03 get pod archive -o jsonpath='{.status.podIP}')
kubectl get namespaces -l division=science
kubectl -n survey-031-010-03-03 exec mapper -- python /app/client.py tcp "$ARCHIVE_IP" 8080
kubectl -n outpost-031-010-03-03 exec mapper -- python /app/client.py tcp "$ARCHIVE_IP" 8080
```

The request from `survey-031-010-03-03` must print `open` and the request from `outpost-031-010-03-03` must print `blocked`.

The `mapper` pods in the two labelled namespaces get a reply, because their namespaces match the selector. The `mapper` pod in `outpost-031-010-03-03` times out, because its namespace has no `division=science` label.

When you are done, remove the lab with `astrona destroy ats-031-lab-010-03-03`.

## Common pitfalls

> [!WARNING]
> Anyone who can label namespaces can join the group. In a real cluster, limit who may change namespace labels.
>
> A `namespaceSelector: {}` matches every namespace. Always name a label.
