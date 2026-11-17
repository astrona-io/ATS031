---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Find The Policy That Blocks A Request Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-01-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-01-04" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

Policies add up: a connection works when the sender is allowed to send it and the receiver is allowed to receive it. Under `default-deny-all` both sides are isolated, so a request needs an egress rule on the client and an ingress rule on the server. Start by listing the policies and reading which of them select each pod.

List the policies and look at the one on the receiving pod:

```sh
kubectl -n outpost-031-010-01-04 get networkpolicy
kubectl -n outpost-031-010-01-04 get networkpolicy depot-ingress -o yaml
```

The `lander-egress` policy already allows `lander` to send to the `depot` pods on TCP port 8080. The `depot-ingress` policy admits pods with the label `app: landr`, which matches no pod: the label is misspelled. Fix the label and keep everything else.

Save this as `networkpolicy-depot-ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: depot-ingress
  namespace: outpost-031-010-01-04
spec:
  podSelector:
    matchLabels:
      app: depot
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: lander
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-depot-ingress.yaml
```

Then check the result. The test client prints `open` with the reply, or `blocked` when the connection times out. Use pod IP addresses:

```sh
DEPOT_IP=$(kubectl -n outpost-031-010-01-04 get pod depot -o jsonpath='{.status.podIP}')
kubectl -n outpost-031-010-01-04 exec lander -- python /app/client.py tcp "$DEPOT_IP" 8080
kubectl -n outpost-031-010-01-04 exec stray -- python /app/client.py tcp "$DEPOT_IP" 8080
```

The first command must print `open` and the second `blocked`.

The request now succeeds, because the egress rule on `lander` and the repaired ingress rule on `depot` both match it. The `stray` pod still times out to `depot`, and `lander` still times out to `stray`, because `default-deny-all` stays in place and no rule allows those paths.

When you are done, remove the lab with `astrona destroy ats-031-lab-010-01-04`.

## Common pitfalls

> [!WARNING]
> A selector that matches no pod is valid YAML and the API server accepts it. Compare the selector with the real labels from `kubectl get pods --show-labels`.
>
> Do not delete `default-deny-all` to make the request work. That opens every path in the namespace.
