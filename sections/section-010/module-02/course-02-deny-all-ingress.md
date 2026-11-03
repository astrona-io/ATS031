---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Deny All Ingress

The most common baseline stops all incoming connections to every pod in a namespace. It protects servers, because nothing can reach them until an allow rule opens a path. This part writes that policy, applies it to `outpost`, and proves its effect with requests from two directions.

## The policy

A default-deny ingress policy has an empty `podSelector` and lists `Ingress` in `policyTypes`. An empty `podSelector: {}` selects every pod in the namespace of the policy. The policy has no `ingress` section, so the list of allowed sources is empty and nothing is allowed. Write `policyTypes` out even though Kubernetes can infer it. When the field is missing, Kubernetes sets the type from the sections that exist, and a policy with no `egress` section never isolates egress.

<!-- astrona:playground:renew -->

Save this as `networkpolicy-default-deny-ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: outpost
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

Apply it:

```sh
kubectl apply -f networkpolicy-default-deny-ingress.yaml
```

Then check the result. The first request comes from a pod in another namespace, and the second comes from a pod in the same namespace. Both target the `probe` Service in `outpost`. Both must stop after three seconds with a timeout, because the ingress side of the `probe` pods is now isolated and no rule allows any source.

```sh
kubectl -n starfleet exec shuttle -- wget -q -T 3 -O- http://probe.outpost/
kubectl -n outpost exec shuttle -- wget -q -T 3 -O- http://probe/
```

Both failures are timeouts, not refusals. A refusal means that a host answered with a reset, and a timeout means the network plugin dropped the packets. The second request shows that a baseline also blocks traffic inside the namespace. The `shuttle` pod and the `probe` pods share a namespace, and the policy still stops the connection.

## What the baseline does not change

The policy lists only `Ingress`, so egress stays open for every pod in `outpost`. Prove it: the `shuttle` pod in `outpost` can still send a request to a pod in a namespace without a policy.

```sh
kubectl -n outpost exec shuttle -- wget -q -T 3 -O- http://probe.dock/
```

The request returns the `probe` response from `dock`. The reply to that request also works in the other direction, even though `outpost` denies ingress. The network plugin tracks each connection, and the reply to an allowed connection is allowed automatically. Ingress policy applies to new incoming connections, not to replies.

## Reading the policy back

Use `describe` to see how the cluster understands the policy. The output states which pods the policy selects, the allowed incoming traffic and the policy types.

```sh
kubectl -n outpost describe networkpolicy default-deny-ingress
```

The output reports that all pods in the namespace are selected, that no incoming traffic is allowed and that the policy affects ingress. If the output mentions a different policy type than you expect, check the `policyTypes` field first.

## A variant that looks the same

Some tutorials write the baseline with an empty ingress rule, `ingress: [{}]`. That policy allows all traffic and is the opposite of a baseline. The difference is one pair of brackets, so always read the section. A missing `ingress` section with `policyTypes: [Ingress]` means "allow nothing". An `ingress` entry with no fields means "allow everything".

You can now deny all incoming traffic in a namespace and prove it from two directions. Egress is still open, which leaves a compromised pod free to send requests anywhere. The next part closes that direction and shows the first thing that breaks when you do.

## Common pitfalls

> [!WARNING]
> - **Writing `ingress: [{}]`.** An empty rule allows all sources. The baseline has no `ingress` section.
> - **Putting the policy in the wrong namespace.** A policy selects pods only in its own namespace.
> - **Expecting the baseline to block egress.** Ingress and egress are separate directions.
> - **Testing with a pod that does not exist or is not ready.** A failed request from a missing pod proves nothing. Check the client first.
