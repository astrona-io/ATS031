---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow One Peer And Deny Another Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-01-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Inspect And Explain

The application and client fixtures are healthy. Complete the required change without replacing unrelated resources.

Inspect the relevant evidence:

```sh
kubectl -n starfleet get pods --show-labels
kubectl -n outpost get pods --show-labels
kubectl -n starfleet get networkpolicy -o yaml
```

A NetworkPolicy selects destination Pods and describes allowed ingress. A Pod selector in a peer rule without a namespace selector matches only that policy namespace. The policy-capable network plugin enforces the rule. A negative request must fail with a network timeout, not because the client Pod is absent.


Save this as `networkpolicy-probe-shuttle.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: probe-shuttle
  namespace: starfleet
spec:
  podSelector:
    matchLabels:
      app: probe
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: shuttle
    ports:
    - protocol: TCP
      port: 8080
```

Apply the required change:

```sh
kubectl apply -f networkpolicy-probe-shuttle.yaml
```

## Verify The Result

Observe the actual result. A denied-request command returns a nonzero status when the denial works. Run denial checks separately from a shell sequence that stops on the first nonzero status.

```sh
kubectl -n starfleet exec shuttle -- wget -q -T 3 -O- http://probe/
kubectl -n outpost exec drifter -- wget -q -T 3 -O- http://probe.starfleet/
```

Create NetworkPolicy `probe-shuttle` selecting `app: probe` for ingress. Allow only same-namespace Pods labelled `app: shuttle` on TCP port 8080. Keep the original workload and clients healthy. Shuttle must receive version one through the Service; drifter in `outpost` must time out. Do not create any policy that also allows drifter.

After recording the result, remove this independent lab with `astrona destroy ats-031-lab-010-01-01`.

## Common pitfalls

> [!WARNING]
> Policies combine their allowed traffic. Check a denied peer as well as an allowed peer. A missing client or refused listener is not evidence that the network policy enforced a timeout.
