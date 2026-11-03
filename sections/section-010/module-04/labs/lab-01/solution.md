---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Repair A Broken Policy Set Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-04-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-04-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Inspect and explain

Run the script and read the policies. The script shows which of the three needs fails.

```sh
kubectl -n starfleet exec scout -- python /app/check.py
kubectl -n starfleet get networkpolicy
kubectl -n starfleet describe networkpolicy scout-egress scout-to-probe probe-ingress
kubectl get namespace starfleet --show-labels
```

Three kinds of fault explain the result. DNS fails because no policy lets `scout` reach CoreDNS, and the existing `scout-egress` policy holds only the API server rule. The `probe` step fails because `scout-to-probe` selects the namespace by a label named `name`, which the namespace does not have, and because `probe-ingress` has the type `Egress` with a peer that selects a mistyped pod label, so nothing opens ingress to the `probe` pods. The `api` step already works through the existing rule.

Save this as `networkpolicy-scout-dns.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: scout-dns
  namespace: starfleet
spec:
  podSelector:
    matchLabels:
      app: scout
  policyTypes:
  - Egress
  egress:
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
kubectl apply -f networkpolicy-scout-dns.yaml
```

Save this as `networkpolicy-scout-to-probe.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: scout-to-probe
  namespace: starfleet
spec:
  podSelector:
    matchLabels:
      app: scout
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: starfleet
      podSelector:
        matchLabels:
          app: probe
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-scout-to-probe.yaml
```

Save this as `networkpolicy-probe-ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: probe-ingress
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
          app: scout
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-probe-ingress.yaml
```

## Verify the result

The script must print `dns=ok probe=ok api=ok`. The two requests from `drifter` must time out. Run the checks one by one.

```sh
kubectl -n starfleet exec scout -- python /app/check.py
PROBE_IP=$(kubectl -n starfleet get pod -l app=probe -o jsonpath='{.items[0].status.podIP}')
SCOUT_IP=$(kubectl -n starfleet get pod scout -o jsonpath='{.status.podIP}')
kubectl -n outpost exec drifter -- wget -q -T 3 -O- "http://$PROBE_IP:8080/"
kubectl -n outpost exec drifter -- wget -q -T 3 -O- "http://$SCOUT_IP:8080/"
```

After recording the result, remove this independent lab with `astrona destroy ats-031-lab-010-04-01`.

## Common pitfalls

> [!WARNING]
> - **Fixing one fault and stopping.** Faults hide each other. Run the script after each change.
> - **Deleting `default-deny-all`.** That opens every pod and breaks the limits of the task.
> - **Opening everything to pass the script.** A rule without peers or ports fails the grader.
> - **Skipping the denied requests.** A repair that also lets `drifter` in is a leak.
