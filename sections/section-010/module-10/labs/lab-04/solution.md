# Find The Policy That Blocks A Request — Solution

You solve this lab by repairing one NetworkPolicy. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

List the pods with their labels and the policies in the namespace:

```sh
kubectl -n outpost-031-010-01-04 get pods --show-labels
kubectl -n outpost-031-010-01-04 get networkpolicy
```

The pods carry `app: lander`, `app: depot` and `app: stray`. Three policies exist: `default-deny-all`, `lander-egress` and `depot-ingress`.

Policies add up. A connection works only when the sender is allowed to send it and the receiver is allowed to receive it. `default-deny-all` selects every pod for both directions, so the request needs an egress rule on `lander` and an ingress rule on `depot`. Read both:

```sh
kubectl -n outpost-031-010-01-04 get networkpolicy lander-egress -o yaml
kubectl -n outpost-031-010-01-04 get networkpolicy depot-ingress -o yaml
```

`lander-egress` already allows `lander` to send to the `depot` pods on TCP port 8080. `depot-ingress` admits pods with the label `app: landr`, which matches no pod: the label is misspelled. The API server accepts a selector that matches nothing, so the mistake shows only in the traffic.

## Step 2: repair depot-ingress (check `lander-reaches-depot`)

Fix the label in `depot-ingress` and keep everything else, including the name and the port.

Save this as `networkpolicy-depot-ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: depot-ingress
  namespace: outpost-031-010-01-04
spec:
  podSelector:
    matchLabels:
      app: depot
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: lander
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-depot-ingress.yaml
```

Then test the request. Every pod has a small test client. It prints `open` with the reply, or `blocked` when the connection times out. Use pod IP addresses:

```sh
DEPOT_IP=$(kubectl -n outpost-031-010-01-04 get pod depot -o jsonpath='{.status.podIP}')
kubectl -n outpost-031-010-01-04 exec lander -- python /app/client.py tcp "$DEPOT_IP" 8080
```

It must print `open`. The egress rule on `lander` and the repaired ingress rule on `depot` now both match the request.

## Step 3: confirm the baseline and the narrow rules (check `baseline-and-narrow-rules`)

The repair must not weaken anything else. `default-deny-all` must still select every pod for both directions with no rules, and only the three original policies may exist:

```sh
kubectl -n outpost-031-010-01-04 get networkpolicy
kubectl -n outpost-031-010-01-04 get networkpolicy default-deny-all -o yaml
```

The list must show exactly `default-deny-all`, `depot-ingress` and `lander-egress`. The `default-deny-all` policy must still have `podSelector: {}`, list `Ingress` and `Egress`, and have no `ingress` or `egress` rules. The rule in `depot-ingress` admits only pods labelled `app: lander` in the same namespace, on TCP port 8080 only.

## Step 4: test the paths that must stay closed (check `other-paths-blocked`)

No rule allows `stray` to reach `depot`, and no rule allows `lander` to reach `stray`:

```sh
STRAY_IP=$(kubectl -n outpost-031-010-01-04 get pod stray -o jsonpath='{.status.podIP}')
kubectl -n outpost-031-010-01-04 exec stray -- python /app/client.py tcp "$DEPOT_IP" 8080
kubectl -n outpost-031-010-01-04 exec lander -- python /app/client.py tcp "$STRAY_IP" 8080
```

Both commands must print `blocked`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not delete `default-deny-all` or add rules to it to make the request work. That opens other paths in the namespace, and the task requires the baseline unchanged.
>
> Do not create a new policy for `lander` and leave the broken one in place. Repair `depot-ingress` in place, so only the three original policies exist.
>
> Do not widen the repaired rule: no rule without `ports`, no empty `podSelector`, no `namespaceSelector: {}`, no `ipBlock`, and only TCP port 8080. The peer must match `lander` and not `stray`.
>
> Do not change `lander-egress`. It must still allow only TCP port 8080 to the `depot` pods in `outpost-031-010-01-04`.
