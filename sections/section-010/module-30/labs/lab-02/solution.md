# Repair A Two-Entry Peer Rule — Solution

You solve this lab by changing one NetworkPolicy. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the pod labels and read the current policy:

```sh
kubectl -n dock-031-010-03-02 get pods --show-labels
kubectl -n starfleet-031-010-03-02 get pods --show-labels
kubectl -n outpost-031-010-03-02 get pods --show-labels
kubectl -n dock-031-010-03-02 get networkpolicy assay-from-starfleet -o yaml
```

Three pods carry `app: sampler`, one in each namespace. The `from` list of the policy has two items, each starting with `- `: a `namespaceSelector` for `starfleet-031-010-03-02` and a separate `podSelector` for `app: sampler`.

Two peer entries are joined with OR. The first entry admits every pod in `starfleet-031-010-03-02`, so the `idler` pod gets in. The second entry has no `namespaceSelector`, so it matches `app: sampler` pods in the policy's own namespace, `dock-031-010-03-02`. That is why the local `sampler` gets in.

## Step 2: merge the two entries into one (check `assay-policy-repaired`)

Put both selectors in one peer entry. In one entry they are joined with AND: the sender must be in `starfleet-031-010-03-02` and also carry `app: sampler`. Keep the name, so `kubectl apply` changes the existing policy instead of adding a second one.

Save this as `networkpolicy-assay-from-starfleet.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: assay-from-starfleet
  namespace: dock-031-010-03-02
spec:
  podSelector:
    matchLabels:
      app: assay
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: starfleet-031-010-03-02
      podSelector:
        matchLabels:
          app: sampler
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-assay-from-starfleet.yaml
```

`kubectl apply` replaces the `from` list with the one in your file. Read the policy again with `-o yaml` and count the peer entries: there must be one.

## Step 3: test the senders in starfleet (check `idler-denied`)

Every pod has a small test client. It prints `open` with the reply, or `blocked` when the connection times out:

```sh
ASSAY_IP=$(kubectl -n dock-031-010-03-02 get pod assay -o jsonpath='{.status.podIP}')
kubectl -n starfleet-031-010-03-02 exec sampler -- python /app/client.py tcp "$ASSAY_IP" 8080
kubectl -n starfleet-031-010-03-02 exec idler -- python /app/client.py tcp "$ASSAY_IP" 8080
```

The first command must print `open`. The second must print `blocked`: the `idler` pod is in the right namespace but fails the pod label.

## Step 4: test the sampler pods in other namespaces (check `only-starfleet-sampler`)

Now send the same request from the two `sampler` pods that must stay out:

```sh
kubectl -n dock-031-010-03-02 exec sampler -- python /app/client.py tcp "$ASSAY_IP" 8080
kubectl -n outpost-031-010-03-02 exec sampler -- python /app/client.py tcp "$ASSAY_IP" 8080
```

Both must print `blocked`. These pods carry the right label, but their namespaces do not match the `namespaceSelector`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Every peer entry needs both a `namespaceSelector` and a `podSelector`. A `- ` in front of `podSelector` starts a second entry again, and the two entries are joined with OR.
>
> Do not delete the policy and create one with a new name, and do not add a second policy. The task allows only `assay-from-starfleet` in `dock-031-010-03-02` and no policy in the other namespaces.
>
> Do not use `namespaceSelector: {}` or leave out `ports`. The first matches every namespace, the second allows every port; this task allows only TCP 8080.
