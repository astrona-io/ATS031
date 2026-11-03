---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow One Pod From Another Namespace Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-03-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Inspect and explain

Check the labels the policy relies on. The namespace carries only the automatic name label, and the pods carry `app` labels.

```sh
kubectl get namespace outpost --show-labels
kubectl -n outpost get pods --show-labels
```

The policy selects the `probe` pods in `starfleet`. Its single `from` entry combines the namespace and the pod selector, so a peer must match both. The port is the pod port 8080, because the plugin applies policy to the pod after the Service address has been translated.

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
      podSelector:
        matchLabels:
          app: shuttle
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-probe-from-outpost.yaml
```

## Verify the result

The first request must return the `probe` response. The other three must time out. A denied request returns a nonzero status, so run the checks one by one.

```sh
kubectl -n outpost exec shuttle -- wget -q -T 3 -O- http://probe.starfleet/
kubectl -n outpost exec drifter -- wget -q -T 3 -O- http://probe.starfleet/
kubectl -n dock exec shuttle -- wget -q -T 3 -O- http://probe.starfleet/
kubectl -n starfleet exec shuttle -- wget -q -T 3 -O- http://probe/
```

After recording the result, remove this independent lab with `astrona destroy ats-031-lab-010-03-01`.

## Common pitfalls

> [!WARNING]
> - **Writing two list entries.** A dash before `podSelector` makes it a second entry that allows every `shuttle` pod in `starfleet`.
> - **Selecting the namespace by a made-up label.** Use `kubernetes.io/metadata.name`.
> - **Allowing the Service port.** The policy sees the pod port 8080, not port 80.
> - **Testing only the allowed request.** Run the denied requests too.
