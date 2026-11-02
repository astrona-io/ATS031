---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Default Deny And Troubleshooting Policies

The policies so far each protect a named application. A secure namespace starts from the opposite point: it denies all traffic first and then adds an allowance per need. This part shows the default-deny policy, what it breaks, and a method to find the cause when a request is blocked or unexpectedly allowed.

## Default deny

A default-deny policy selects every pod in a namespace and lists no allowed traffic. Because `podSelector: {}` selects all pods in the namespace and the rules are empty, every pod becomes isolated and nothing is allowed. Existing allow policies still work, because allowances from all policies are combined. A new application pod is protected from its first second, with no policy of its own.

Save this as `networkpolicy-default-deny-all.yaml`:

<!-- astrona:playground:renew -->

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: starfleet
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

Then check the result. The two policies you created before are still present, and the new policy isolates every pod in `starfleet` for ingress and egress. The `shuttle` pod already has an egress allowance, so the lookup and the request still work. The new policy also isolates `blocked-server`, which now has no ingress rule at all.

```sh
kubectl -n starfleet get networkpolicy
kubectl -n starfleet exec shuttle -- wget -q -T 3 -O- http://probe/
```

The request to `probe` still works, because `shuttle-egress` allows it and `probe-shuttle` allows the same connection on the destination side. The union of all policies, not the newest policy, decides.

## Reading a blocked request step by step

When a request fails, do not guess. Follow the same order each time.

First, name the source pod, the destination pod and the port the pod listens on. Second, list the policies in both namespaces and read which pods each selects:

```sh
kubectl get networkpolicy --all-namespaces
kubectl -n starfleet describe networkpolicy probe-shuttle
```

Third, compare the selectors with the real labels. A typing error in a label selects no pods, and the policy then protects nothing:

```sh
kubectl -n starfleet get pods --show-labels
kubectl get namespaces --show-labels
```

Fourth, decide for each side whether it is isolated and whether a rule allows the connection, checking the source egress first and then the destination ingress. Fifth, read the failure type. A timeout means a packet filter dropped it. A refusal means the destination answered and no process listens on that port. A resolution error means the DNS step failed before any connection.

## Proving the cause by removing it

When you suspect one policy, remove it and repeat the request. Deleting a policy takes effect within seconds, and you can apply the same file again. Delete `default-deny-all` now, since it was only a demonstration, and check that nothing else changed:

```sh
kubectl -n starfleet delete -f networkpolicy-default-deny-all.yaml
kubectl -n starfleet get networkpolicy
```

The list shows the two policies `probe-shuttle` and `shuttle-egress` again. If a request starts working after you delete a policy, that policy was the block. If it still fails, the cause is elsewhere: a label, a port, DNS or another policy.

## Where the checks run

Use the client pod that matters for the question. A `kubectl port-forward` connection is made by the kubelet on the node and does not behave like a request from another pod, so it is not a test of a policy. For an exam task, always test from a pod in the namespace the task names.

Policies are namespaced objects. A policy in `outpost` selects only pods in `outpost`. To isolate pods in `starfleet`, the policy must be in `starfleet`, even when the allowed source is in another namespace.

You can now write allow policies, a default-deny policy and a method to explain any blocked or allowed request. The checks above are what you should run before you trust a policy.

## Common pitfalls

> [!WARNING]
> - **Applying default deny without DNS.** Egress default deny also blocks name resolution. Every pod in the namespace then fails to resolve names until a DNS rule exists.
> - **Putting the policy in the wrong namespace.** A policy selects only pods in its own namespace.
> - **Believing the newest policy wins.** Policies add up. Remove the policy that grants the unwanted access.
> - **Reading the policy name.** A policy named `allow-probe` can allow more than the name says. Read the selectors and ports.
