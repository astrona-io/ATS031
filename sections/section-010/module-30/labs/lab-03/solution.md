# Admit A Group Of Namespaces By Label — Solution

You solve this lab with two namespace labels and one NetworkPolicy. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the namespace labels, the pods, and that no policy exists yet:

```sh
kubectl get namespaces --show-labels
kubectl -n starfleet-031-010-03-03 get pods --show-labels
kubectl get networkpolicy -A
```

No namespace has a `division` label yet. Without any policy, every `mapper` pod can reach the `archive` pod.

## Step 2: label the science namespaces (check `division-labels`)

A `namespaceSelector` with a label you choose admits a group of namespaces. Any namespace that gets the label later joins the group without a change to the policy. Label the two namespaces first:

```sh
kubectl label namespace survey-031-010-03-03 division=science --overwrite
kubectl label namespace salvage-031-010-03-03 division=science --overwrite
```

Then check the group:

```sh
kubectl get namespaces -l division=science
```

The list must show `survey-031-010-03-03` and `salvage-031-010-03-03`, and not `outpost-031-010-03-03`.

## Step 3: admit the group with a namespaceSelector (check `archive-policy`)

The peer entry has only a `namespaceSelector`. With no `podSelector` in the entry, it matches every pod in the selected namespaces. The `ports` list limits the rule to TCP 8080.

Save this as `networkpolicy-archive-from-science.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: archive-from-science
  namespace: starfleet-031-010-03-03
spec:
  podSelector:
    matchLabels:
      app: archive
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          division: science
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-archive-from-science.yaml
```

## Step 4: test the three mapper pods (check `archive-admits-division`)

Every pod has a small test client. It prints `open` with the reply, or `blocked` when the connection times out:

```sh
ARCHIVE_IP=$(kubectl -n starfleet-031-010-03-03 get pod archive -o jsonpath='{.status.podIP}')
kubectl -n survey-031-010-03-03 exec mapper -- python /app/client.py tcp "$ARCHIVE_IP" 8080
kubectl -n salvage-031-010-03-03 exec mapper -- python /app/client.py tcp "$ARCHIVE_IP" 8080
kubectl -n outpost-031-010-03-03 exec mapper -- python /app/client.py tcp "$ARCHIVE_IP" 8080
```

The first two commands must print `open`, because their namespaces match the selector. The last one must print `blocked`, because `outpost-031-010-03-03` has no `division=science` label.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Select the namespaces by `division: science`, not by `kubernetes.io/metadata.name`. A name selector admits fixed namespaces, not the group.
>
> Do not add a `podSelector` with labels to the peer entry. The task admits every pod in the science namespaces; only an empty `podSelector: {}` or none at all does that.
>
> A `namespaceSelector: {}` matches every namespace, and a rule without `ports` allows every port. Always name the label and TCP 8080.
>
> Anyone who can label namespaces can join the group. In a real cluster, limit who may change namespace labels.
