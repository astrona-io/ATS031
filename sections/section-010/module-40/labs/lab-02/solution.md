# Allow Only DNS Egress Under A Baseline — Solution

You solve this lab with one NetworkPolicy. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the pod labels, the baseline policy and the CoreDNS pods:

```sh
kubectl -n starfleet-031-010-04-02 get pods --show-labels
kubectl -n starfleet-031-010-04-02 get networkpolicy default-deny-all -o yaml
kubectl -n kube-system get pods -l k8s-app=kube-dns
kubectl get namespace kube-system --show-labels
```

`default-deny-all` selects every pod for ingress and egress and has no rules. Under it, a pod cannot even send a DNS query to CoreDNS, the cluster DNS server. The `kube-system` namespace carries the automatic label `kubernetes.io/metadata.name: kube-system`.

## Step 2: allow DNS egress for navigator only (check `dns-rule`)

The policy selects only `app: navigator` and lists only `Egress` in `policyTypes`, so it adds outgoing traffic for that one pod. Its rule has one peer entry with a `namespaceSelector` and a `podSelector` together: the packet must go to a pod labelled `k8s-app: kube-dns` that runs in `kube-system`. The `ports` list allows UDP and TCP port 53 and nothing else.

Save this as `networkpolicy-navigator-dns.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: navigator-dns
  namespace: starfleet-031-010-04-02
spec:
  podSelector:
    matchLabels:
      app: navigator
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
kubectl apply -f networkpolicy-navigator-dns.yaml
```

## Step 3: navigator resolves names (check `navigator-resolves`)

The `navigator` pod now sends its query to CoreDNS on port 53, and the answer comes back on the same connection. Policies allow reply packets of an allowed connection, so no ingress rule is needed for the answer.

## Step 4: test that DNS is the only path (checks `navigator-resolves` and `dns-only`)

Every pod has a small test client. It prints `open` with the reply, `blocked` when the connection times out, and `resolved` or `unresolved` for a DNS lookup:

```sh
COREDNS_IP=$(kubectl -n kube-system get pods -l k8s-app=kube-dns -o jsonpath='{.items[0].status.podIP}')
CARGO_IP=$(kubectl -n starfleet-031-010-04-02 get pod cargo -o jsonpath='{.status.podIP}')
kubectl -n starfleet-031-010-04-02 exec navigator -- python /app/client.py dns kubernetes.default.svc.cluster.local
kubectl -n starfleet-031-010-04-02 exec navigator -- python /app/client.py tcp "$COREDNS_IP" 9153
kubectl -n starfleet-031-010-04-02 exec navigator -- python /app/client.py tcp "$CARGO_IP" 8080
kubectl -n starfleet-031-010-04-02 exec cargo -- python /app/client.py dns kubernetes.default.svc.cluster.local
```

The first command must print `resolved`. The next two must print `blocked`: port 9153 is the CoreDNS metrics port, not DNS, and the rule allows only port 53. The last command must print `unresolved`, because the policy does not select `cargo`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Allow both UDP and TCP port 53. Large DNS answers switch to TCP, and a UDP-only rule fails the check.
>
> A rule `to` CoreDNS without `ports` allows every port on those pods, including 9153. Always list the ports.
>
> Put the `namespaceSelector` and the `podSelector` in one peer entry. As two separate entries (two `-` items), they mean "any pod in `kube-system`" or "any `kube-dns` pod in `starfleet-031-010-04-02`", and the check fails. `namespaceSelector: {}` matches every namespace.
>
> Do not change `default-deny-all` and do not add a second policy. A selector that also matches `cargo` fails the check.
