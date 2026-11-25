---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Isolate One Pod For Egress Only Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-01-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-01-03" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

A pod is isolated for a direction when at least one policy selects it and lists that direction in `policyTypes`. A policy that lists only `Egress` and has no `egress` rules blocks every connection the pod opens, including DNS lookups, while incoming connections stay as they were.

Write `policyTypes` explicitly. If you leave it out, the API server fills it in from the rule sections you wrote: a policy with no rules would then get only `Ingress`, which is the opposite of what this task needs.

Save this as `networkpolicy-relay-egress-isolation.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: relay-egress-isolation
  namespace: starfleet-031-010-01-03
spec:
  podSelector:
    matchLabels:
      app: relay
  policyTypes:
  - Egress
```

Apply it:

```sh
kubectl apply -f networkpolicy-relay-egress-isolation.yaml
```

Then check the result. The test client prints one word for each attempt: `open` with the reply, `blocked` when the connection times out, `refused` when nothing listens, or `resolved` and `unresolved` for a DNS lookup. Use pod IP addresses, so DNS and traffic are tested separately:

```sh
LANDER_IP=$(kubectl -n starfleet-031-010-01-03 get pod lander -o jsonpath='{.status.podIP}')
RELAY_IP=$(kubectl -n starfleet-031-010-01-03 get pod relay -o jsonpath='{.status.podIP}')
kubectl -n starfleet-031-010-01-03 exec relay -- python /app/client.py tcp "$LANDER_IP" 8080
kubectl -n starfleet-031-010-01-03 exec relay -- python /app/client.py dns kubernetes.default.svc.cluster.local
kubectl -n starfleet-031-010-01-03 exec courier -- python /app/client.py tcp "$RELAY_IP" 8080
```

The first two commands must print `blocked` and `unresolved`. The last command must still print `open`.

The `relay` pod times out to the `lander` pod and cannot resolve names, because the policy isolates it for egress with no rules. The `courier` pod still reaches the `relay` pod, because the policy does not list `Ingress`. The `lander` and `courier` pods are not selected, so nothing changes for them.

When you are done, remove the lab with `astrona destroy ats-031-lab-010-01-03`.

## Common pitfalls

> [!WARNING]
> A policy without `policyTypes` and without rules isolates the pod for ingress only. Always write `policyTypes` when you mean egress.
>
> Egress isolation also stops DNS. A lookup that prints `unresolved` is expected here and is not a CoreDNS fault.
