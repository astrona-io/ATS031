---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Repair A Two-Entry Peer Rule Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-03-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-03-02" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Inspect and explain

Read the existing policy and test the paths. The request tests show which pods get through.

```sh
kubectl -n outpost-031-010-03-02 get networkpolicy probe-from-starfleet -o yaml
kubectl -n starfleet-031-010-03-02 exec drifter -- wget -q -T 3 -O- http://probe.outpost-031-010-03-02/
kubectl -n outpost-031-010-03-02 exec shuttle -- wget -q -T 3 -O- http://probe.outpost-031-010-03-02/
```

The `from` list has two entries: one `namespaceSelector` and one `podSelector`, each started by its own dash. The first entry allows every pod in `starfleet-031-010-03-02`. The second allows every `shuttle` pod in `outpost-031-010-03-02`. Both requests above are therefore allowed, and the task wants neither. The repair puts both selectors into one entry. Applying the corrected file with the same name replaces the rule list.

Save this as `networkpolicy-probe-from-starfleet.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: probe-from-starfleet
  namespace: outpost-031-010-03-02
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
          kubernetes.io/metadata.name: starfleet-031-010-03-02
      podSelector:
        matchLabels:
          app: shuttle
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-probe-from-starfleet.yaml
```

## Verify the result

The first request must return the `probe` response. The other three must time out. Run the checks one by one.

```sh
kubectl -n starfleet-031-010-03-02 exec shuttle -- wget -q -T 3 -O- http://probe.outpost-031-010-03-02/
kubectl -n starfleet-031-010-03-02 exec drifter -- wget -q -T 3 -O- http://probe.outpost-031-010-03-02/
kubectl -n outpost-031-010-03-02 exec shuttle -- wget -q -T 3 -O- http://probe.outpost-031-010-03-02/
kubectl -n dock-031-010-03-02 exec shuttle -- wget -q -T 3 -O- http://probe.outpost-031-010-03-02/
```

After recording the result, remove this independent lab with `astrona destroy ats-031-lab-010-03-02`.

## Common pitfalls

> [!WARNING]
> - **Adding a deny policy.** Policies only add; nothing can subtract a path that another policy allows.
> - **Leaving the extra dash.** One dash too many keeps two entries.
> - **Fixing the selector but not testing the denied pods.** Test `drifter` and the same-namespace `shuttle`.
> - **Creating a second policy.** The old policy would keep allowing the wide paths.
