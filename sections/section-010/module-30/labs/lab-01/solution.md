# Allow One Pod From Another Namespace — Solution

You solve this lab with one NetworkPolicy. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the pod labels, the namespace labels, and that no policy exists yet:

```sh
kubectl -n starfleet-031-010-03-01 get pods --show-labels
kubectl -n outpost-031-010-03-01 get pods --show-labels
kubectl -n dock-031-010-03-01 get pods --show-labels
kubectl get namespace outpost-031-010-03-01 --show-labels
kubectl get networkpolicy -A
```

Three pods carry `app: courier`, one in each namespace. Every namespace has the label `kubernetes.io/metadata.name: <namespace name>`, which the API server sets on its own. Without any policy, every pod can reach every other pod.

## Step 2: write one combined peer entry (check `registry-policy`)

A peer entry in `from` can hold a `namespaceSelector` and a `podSelector` together. In one entry they are joined with AND: the sender must be in a selected namespace and also carry the selected pod label. This is the way to admit one pod from one other namespace.

Select the namespace by `kubernetes.io/metadata.name`. This label always exists and matches exactly one namespace. The `ports` list limits the rule to TCP 8080, the port the `registry` pod listens on.

Save this as `networkpolicy-registry-from-outpost-courier.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: registry-from-outpost-courier
  namespace: starfleet-031-010-03-01
spec:
  podSelector:
    matchLabels:
      app: registry
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: outpost-031-010-03-01
      podSelector:
        matchLabels:
          app: courier
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-registry-from-outpost-courier.yaml
```

Look at the indentation: `podSelector` has no `- ` in front of it, so it belongs to the same entry as `namespaceSelector`.

## Step 3: test the allowed sender (check `outpost-courier-allowed`)

Every pod has a small test client. It prints `open` with the reply, or `blocked` when the connection times out:

```sh
REGISTRY_IP=$(kubectl -n starfleet-031-010-03-01 get pod registry -o jsonpath='{.status.podIP}')
kubectl -n outpost-031-010-03-01 exec courier -- python /app/client.py tcp "$REGISTRY_IP" 8080
```

The command must print `open`. The `courier` pod in `outpost-031-010-03-01` matches both selectors of the peer entry.

## Step 4: test the blocked senders (check `only-outpost-courier`)

Now send the same request from the three pods that must stay out:

```sh
kubectl -n outpost-031-010-03-01 exec idler -- python /app/client.py tcp "$REGISTRY_IP" 8080
kubectl -n dock-031-010-03-01 exec courier -- python /app/client.py tcp "$REGISTRY_IP" 8080
kubectl -n starfleet-031-010-03-01 exec courier -- python /app/client.py tcp "$REGISTRY_IP" 8080
```

All three must print `blocked`. The `idler` pod is in the right namespace but has the wrong label. The two other `courier` pods have the right label, but their namespaces do not match the `namespaceSelector`. A `podSelector` alone would have admitted the `courier` in the policy's own namespace, `starfleet-031-010-03-01`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Indentation decides the meaning. A `- ` in front of `podSelector` starts a second peer entry, and the two entries are joined with OR. Every peer entry must have both selectors.
>
> Do not use `namespaceSelector: {}`. It matches every namespace, so the `courier` pods in `dock-031-010-03-01` and `starfleet-031-010-03-01` would get in.
>
> Do not leave out `ports`. A rule without ports allows every port; this task allows only TCP 8080.
>
> Do not add a second policy, such as a default deny or a policy in `outpost-031-010-03-01` or `dock-031-010-03-01`. The task allows only `registry-from-outpost-courier`.
