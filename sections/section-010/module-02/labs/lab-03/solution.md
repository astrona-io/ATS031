---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Deny All Egress And Observe DNS Fail Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-02-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-02-03" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

A default-deny egress policy selects every pod in a namespace and lists only `Egress` in `policyTypes`, with no rules. The pods can still receive connections, but they cannot open any, not even DNS lookups to CoreDNS.

Save this as `networkpolicy-default-deny-egress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-egress
  namespace: dock-031-010-02-03
spec:
  podSelector: {}
  policyTypes:
  - Egress
```

Apply it:

```sh
kubectl apply -f networkpolicy-default-deny-egress.yaml
```

Then check the result. The test client prints `open` with the reply, `blocked` when the connection times out, and `resolved` or `unresolved` for a DNS lookup:

```sh
PILOT_IP=$(kubectl -n outpost-031-010-02-03 get pod pilot -o jsonpath='{.status.podIP}')
HAULER_IP=$(kubectl -n dock-031-010-02-03 get pod hauler -o jsonpath='{.status.podIP}')
kubectl -n dock-031-010-02-03 exec hauler -- python /app/client.py tcp "$PILOT_IP" 8080
kubectl -n dock-031-010-02-03 exec winch -- python /app/client.py dns kubernetes.default.svc.cluster.local
kubectl -n outpost-031-010-02-03 exec pilot -- python /app/client.py tcp "$HAULER_IP" 8080
```

The first command must print `blocked` and the second `unresolved`. The last one must print `open`, because the reply to an allowed incoming connection is not new egress.

The `hauler` pod times out to the `pilot` pod and its DNS lookup prints `unresolved`, because the pods in `dock-031-010-02-03` may not send anything. The `pilot` pod in `outpost-031-010-02-03` still reaches `hauler`, because the policy does not isolate ingress.

When you are done, remove the lab with `astrona destroy ats-031-lab-010-02-03`.

## Common pitfalls

> [!WARNING]
> After an egress baseline, the first thing that breaks is usually DNS. Add a DNS rule before any other egress rule when the pods use names.
>
> The reply to an allowed incoming connection is not blocked by egress isolation. The network plugin tracks the connection and lets the reply through.
