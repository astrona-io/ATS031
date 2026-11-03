---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Cross-Namespace Ingress

A `podSelector` in a peer matches only pods in the namespace of the policy. To allow a pod in another namespace, the peer needs a `namespaceSelector`. This part protects the `probe` pods in `starfleet` and compares what happens with a `namespaceSelector` alone, and with a `podSelector` alone.

## The problem to solve

The `shuttle` pod in `outpost` should reach the `probe` pods in `starfleet` on port 8080. Nothing else in `outpost` should. The first attempt selects the whole namespace: every pod in `outpost` becomes an allowed source.

<!-- astrona:playground:renew -->

Save this as `networkpolicy-probe-from-outpost.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: probe-from-outpost
  namespace: starfleet
spec:
  podSelector:
    matchLabels:
      app: probe
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: outpost
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-probe-from-outpost.yaml
```

Then check the result. Both clients in `outpost` reach the `probe` Service, because the peer matches every pod of that namespace. The `shuttle` pod in `dock` and the one in `starfleet` do not, because neither matches the peer, and the `probe` pods are now isolated.

```sh
kubectl -n outpost exec shuttle -- wget -q -T 3 -O- http://probe.starfleet/
kubectl -n outpost exec drifter -- wget -q -T 3 -O- http://probe.starfleet/
kubectl -n dock exec shuttle -- wget -q -T 3 -O- http://probe.starfleet/
```

The first two requests return the `probe` response. The third times out. The policy is correct for "everything in `outpost`", and too wide for "only the `shuttle`".

## A podSelector alone stays in its own namespace

Replace the peer with a `podSelector` for `app: shuttle` and nothing else. Save this as `networkpolicy-probe-from-shuttle.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: probe-from-outpost
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

The file uses the same policy name, so applying it replaces the previous rule instead of adding a second policy.

```sh
kubectl apply -f networkpolicy-probe-from-shuttle.yaml
kubectl -n starfleet exec shuttle -- wget -q -T 3 -O- http://probe/
kubectl -n outpost exec shuttle -- wget -q -T 3 -O- http://probe.starfleet/
```

The request from `shuttle` in `starfleet` works. The request from `shuttle` in `outpost` times out, even though the pod has the right label. A `podSelector` without a `namespaceSelector` matches only pods in the policy namespace, here `starfleet`. The Calico plugin applies the rule the same way, because this is behaviour of the API, not of the plugin.

## What each peer form matches

Compare the three forms of one peer entry. Reading them correctly is the main skill for this topic.

| Peer entry | Matches |
| --- | --- |
| `podSelector` only | Pods with the labels, in the namespace of the policy |
| `namespaceSelector` only | All pods in every namespace with the labels |
| Both in one entry | Pods with the pod labels, in namespaces with the namespace labels |

An empty `namespaceSelector: {}` matches all namespaces, and an empty `podSelector: {}` matches all pods in the scope of that entry. The third row is the form that solves the problem of this part, and the next part writes it and shows how easily one dash turns it into something else.

The source address matters too. Calico sees the IP address of the sending pod, so the policy works on pod identity as long as pods talk to each other directly. You now know that a cross-namespace allowance needs a `namespaceSelector`, and that this selector alone opens the whole namespace.

## Common pitfalls

> [!WARNING]
> - **Expecting `podSelector` to cross namespaces.** It never leaves the policy namespace unless a `namespaceSelector` is in the same entry.
> - **Using `namespaceSelector` alone for one pod.** It admits every pod in the matching namespaces.
> - **Applying a second file under a new name.** A new name adds a policy, and the old, wider policy keeps working. Reuse the name to replace.
> - **Testing only from the allowed namespace.** Run the request from a pod in another namespace too.
