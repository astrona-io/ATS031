# Apply One Baseline To Labelled Namespaces — Solution

You solve this lab with two namespace labels and one NetworkPolicy file applied twice. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the namespace labels, the pods, and that no policy exists yet:

```sh
kubectl get namespaces --show-labels
kubectl get pods -A -l 'app in (loader,pump,cook)' -o wide
kubectl get networkpolicy -A
```

No namespace carries a `netpol` label. Each pod carries the label `app: <pod name>` and serves TCP port 8080.

## Step 2: label the restricted namespaces (check `namespaces-labelled`)

A NetworkPolicy is a namespaced object, so a baseline must exist in every namespace that needs it. A label on the namespaces lets you pick them later with one label selector. The label itself changes no traffic.

```sh
kubectl label namespace cargo-031-010-02-05 netpol=restricted
kubectl label namespace fuel-031-010-02-05 netpol=restricted
```

Leave `galley-031-010-02-05` without the label.

## Step 3: apply one baseline to every labelled namespace (check `baseline-per-namespace`)

Write the baseline without a `namespace` field, so the same file fits every namespace. `podSelector: {}` selects every pod, and listing both `Ingress` and `Egress` with no rules isolates them in both directions.

Save this as `networkpolicy-default-deny-all.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

Apply it to every namespace with the label. The `for` loop reads the namespace names from the label selector, and `kubectl -n` sets the namespace for each apply:

```sh
for namespace in $(kubectl get namespaces -l netpol=restricted -o jsonpath='{.items[*].metadata.name}'); do
  kubectl -n "$namespace" apply -f networkpolicy-default-deny-all.yaml
done
```

Then check the result:

```sh
kubectl get namespaces -l netpol=restricted
kubectl get networkpolicy -A
```

The first command lists `cargo-031-010-02-05` and `fuel-031-010-02-05`. The second lists `default-deny-all` in exactly those two namespaces and nothing in `galley-031-010-02-05`.

## Step 4: test the baseline (check `baseline-enforced`)

Every pod has a small test client. It prints `open` with the reply, `blocked` when the connection times out, and `resolved` or `unresolved` for a DNS lookup:

```sh
LOADER_IP=$(kubectl -n cargo-031-010-02-05 get pod loader -o jsonpath='{.status.podIP}')
PUMP_IP=$(kubectl -n fuel-031-010-02-05 get pod pump -o jsonpath='{.status.podIP}')
kubectl -n galley-031-010-02-05 exec cook -- python /app/client.py tcp "$LOADER_IP" 8080
kubectl -n galley-031-010-02-05 exec cook -- python /app/client.py tcp "$PUMP_IP" 8080
kubectl -n fuel-031-010-02-05 exec pump -- python /app/client.py dns kubernetes.default.svc.cluster.local
kubectl -n galley-031-010-02-05 exec cook -- python /app/client.py dns kubernetes.default.svc.cluster.local
```

The first two commands must print `blocked`, the third `unresolved`, and the last must start with `resolved`.

`cook` times out because `loader` and `pump` are isolated for ingress. `pump` cannot reach CoreDNS, the cluster DNS server, because it is isolated for egress. `cook` still resolves names because no policy selects it.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> A label on a namespace does nothing by itself. NetworkPolicy has no cluster-wide object; the label only helps you find the namespaces to apply the policy to.
>
> If the manifest has a `namespace` field, `kubectl -n` with a different namespace fails. Leave the field out of a shared baseline file.
>
> Do not label `galley-031-010-02-05` and do not create any policy there, not even an allow policy. It must stay fully open.
>
> Do not narrow `podSelector`, drop one of the two `policyTypes`, or add rules to `default-deny-all`. Each labelled namespace needs the full baseline.
