---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Apply A Default-Deny Baseline And Allow One Path Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-02-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Inspect and explain

Read the starting state. The pods have the labels the policies select on, and no policy exists yet.

```sh
kubectl -n outpost-031-010-02-01 get pods --show-labels
kubectl get networkpolicy --all-namespaces
```

The baseline comes first. It selects all pods in `outpost-031-010-02-01` and isolates them for both directions. The allow rules then open exactly one path. A connection between two isolated pods needs an egress rule at the source and an ingress rule at the destination, and the `shuttle` pod also needs DNS to resolve the name `probe`.

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

Save this as `networkpolicy-probe-ingress-from-shuttle.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: probe-ingress-from-shuttle
  namespace: outpost-031-010-02-01
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

Apply it:

```sh
kubectl apply -f networkpolicy-probe-ingress-from-shuttle.yaml
```

Save this as `networkpolicy-shuttle-egress-to-probe.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: shuttle-egress-to-probe
  namespace: outpost-031-010-02-01
spec:
  podSelector:
    matchLabels:
      app: shuttle
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: probe
    ports:
    - protocol: TCP
      port: 8080
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
```

Apply it:

```sh
kubectl apply -f networkpolicy-shuttle-egress-to-probe.yaml
```

## Verify the result

The first request must return the `probe` response. The next three must time out or, for the last one, return the response because `starfleet-031-010-02-01` has no policy. A denied request returns a nonzero status, so run the checks one by one.

```sh
kubectl -n outpost-031-010-02-01 exec shuttle -- wget -q -T 3 -O- http://probe/
kubectl -n starfleet-031-010-02-01 exec shuttle -- wget -q -T 3 -O- http://probe.outpost-031-010-02-01/
kubectl -n outpost-031-010-02-01 exec shuttle -- wget -q -T 3 -O- http://probe.starfleet-031-010-02-01/
kubectl -n starfleet-031-010-02-01 exec shuttle -- wget -q -T 3 -O- http://probe/
```

After recording the result, remove this independent lab with `astrona destroy ats-031-lab-010-02-01`.

## Common pitfalls

> [!WARNING]
> - **Writing only one half of the path.** The connection needs egress at `shuttle` and ingress at `probe`.
> - **Forgetting TCP port 53.** DNS needs both UDP and TCP.
> - **Testing only the allowed path.** Run the denied requests too.
> - **Applying the files to the wrong namespace.** The namespace is set inside each file.
