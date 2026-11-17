---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Apply A Default-Deny Baseline And Allow One Path Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-02-01" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

A default-deny baseline is a policy that selects every pod in a namespace (`podSelector: {}`) and isolates both directions with no rules. After it, nothing is allowed, and every path you need must be added on purpose. For one path between two pods in the same namespace you need two rules: an ingress rule on the server and an egress rule on the client.

Start with the baseline. It has no rules, so it allows nothing.

Save this as `networkpolicy-default-deny-all.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: outpost-031-010-02-01
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

Apply it:

```sh
kubectl apply -f networkpolicy-default-deny-all.yaml
```

Now let the `forge` pod accept requests from the `smith` pod.

Save this as `networkpolicy-forge-from-smith.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: forge-from-smith
  namespace: outpost-031-010-02-01
spec:
  podSelector:
    matchLabels:
      app: forge
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: smith
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-forge-from-smith.yaml
```

The `smith` pod is isolated for egress too, so it also needs a rule that lets it send to `forge`.

Save this as `networkpolicy-smith-to-forge.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: smith-to-forge
  namespace: outpost-031-010-02-01
spec:
  podSelector:
    matchLabels:
      app: smith
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: forge
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-smith-to-forge.yaml
```

Then check the result. The test client prints `open` with the reply, `blocked` when the connection times out, and `resolved` or `unresolved` for a DNS lookup:

```sh
FORGE_IP=$(kubectl -n outpost-031-010-02-01 get pod forge -o jsonpath='{.status.podIP}')
kubectl -n outpost-031-010-02-01 exec smith -- python /app/client.py tcp "$FORGE_IP" 8080
kubectl -n dock-031-010-02-01 exec visitor -- python /app/client.py tcp "$FORGE_IP" 8080
kubectl -n outpost-031-010-02-01 exec idler -- python /app/client.py dns kubernetes.default.svc.cluster.local
```

The first command must print `open`, the second `blocked` and the third `unresolved`.

The `smith` pod reaches `forge`, because both the egress rule on `smith` and the ingress rule on `forge` match. The `visitor` pod in `dock-031-010-02-01` times out, because the ingress rule names only `smith`. The `idler` pod cannot resolve names, because the baseline also blocks its DNS traffic and no policy gives it egress.

When you are done, remove the lab with `astrona destroy ats-031-lab-010-02-01`.

## Common pitfalls

> [!WARNING]
> With only the ingress rule on `forge`, the request still times out: the `smith` pod is isolated for egress by the baseline.
>
> A baseline in one namespace does not protect any other namespace. Each namespace needs its own copy.
