---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Deny All Ingress In One Namespace Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-02-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-02-02" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

A default-deny ingress policy selects every pod in a namespace and lists only `Ingress` in `policyTypes`, with no rules. Every pod in the namespace then refuses incoming connections, while outgoing connections stay open.

Save this as `networkpolicy-default-deny-ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: dock-031-010-02-02
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

Apply it:

```sh
kubectl apply -f networkpolicy-default-deny-ingress.yaml
```

Then check the result. The test client prints `open` with the reply, or `blocked` when the connection times out:

```sh
VAULT_IP=$(kubectl -n dock-031-010-02-02 get pod vault -o jsonpath='{.status.podIP}')
VISITOR_IP=$(kubectl -n outpost-031-010-02-02 get pod visitor -o jsonpath='{.status.podIP}')
kubectl -n outpost-031-010-02-02 exec visitor -- python /app/client.py tcp "$VAULT_IP" 8080
kubectl -n dock-031-010-02-02 exec crane -- python /app/client.py tcp "$VAULT_IP" 8080
kubectl -n dock-031-010-02-02 exec crane -- python /app/client.py tcp "$VISITOR_IP" 8080
```

The first two commands must print `blocked`, also the one from the same namespace. The last one must print `open`.

The `visitor` pod in `outpost-031-010-02-02` times out to `vault`, because every pod in `dock-031-010-02-02` is now isolated for ingress. The `crane` pod in `dock-031-010-02-02` still reaches `visitor`, because the policy does not isolate egress.

When you are done, remove the lab with `astrona destroy ats-031-lab-010-02-02`.

## Common pitfalls

> [!WARNING]
> An ingress baseline blocks traffic between pods of the same namespace too, not only traffic from other namespaces.
>
> Without `policyTypes: [Ingress]` and without rules, the API server sets `Ingress` for you. Write it anyway, so a reader sees the intent.
