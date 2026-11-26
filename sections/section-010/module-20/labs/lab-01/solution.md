# Apply A Default-Deny Baseline And Allow One Path — Solution

You solve this lab with three NetworkPolicies. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the labels the policies will use, and that no policy exists yet:

```sh
kubectl -n outpost-031-010-02-01 get pods --show-labels
kubectl -n dock-031-010-02-01 get pods --show-labels
kubectl get networkpolicy -A
```

Each pod carries the label `app: <pod name>` and serves TCP port 8080. Without any policy, every pod can reach every other pod.

## Step 2: isolate every pod (check `default-deny-all`)

A default-deny baseline is a NetworkPolicy that selects every pod in the namespace with `podSelector: {}` and lists both `Ingress` and `Egress` in `policyTypes`, with no rules. A pod selected for a direction accepts only the traffic that some rule allows, and this policy allows nothing. Every path you need after it must be added on purpose.

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

The baseline also blocks egress to CoreDNS, the cluster DNS server, so `idler` can no longer resolve names. That is expected: the task gives `idler` nothing.

## Step 3: let forge accept smith (check `forge-ingress-from-smith`)

For one path between two pods in an isolated namespace you need two rules: an ingress rule on the server and an egress rule on the client. Start with the server. A `from` entry with only a `podSelector` matches pods with that label in the policy's own namespace, so `visitor` in `dock-031-010-02-01` stays out.

Save this as `networkpolicy-forge-from-smith.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: forge-from-smith
  namespace: outpost-031-010-02-01
spec:
  podSelector:
    matchLabels:
      app: forge
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: smith
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-forge-from-smith.yaml
```

## Step 4: let smith send to forge (check `smith-egress-to-forge`)

The baseline isolates `smith` for egress too, so its request still times out with only the ingress rule on `forge`. Add an egress rule on `smith` that names `forge` and TCP port 8080.

Save this as `networkpolicy-smith-to-forge.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: smith-to-forge
  namespace: outpost-031-010-02-01
spec:
  podSelector:
    matchLabels:
      app: smith
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: forge
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-smith-to-forge.yaml
```

## Step 5: test allowed and blocked paths (all checks)

Every pod has a small test client. It prints `open` with the reply, `blocked` when the connection times out, and `resolved` or `unresolved` for a DNS lookup:

```sh
FORGE_IP=$(kubectl -n outpost-031-010-02-01 get pod forge -o jsonpath='{.status.podIP}')
VISITOR_IP=$(kubectl -n dock-031-010-02-01 get pod visitor -o jsonpath='{.status.podIP}')
kubectl -n outpost-031-010-02-01 exec smith -- python /app/client.py tcp "$FORGE_IP" 8080
kubectl -n outpost-031-010-02-01 exec smith -- python /app/client.py tcp "$VISITOR_IP" 8080
kubectl -n dock-031-010-02-01 exec visitor -- python /app/client.py tcp "$FORGE_IP" 8080
kubectl -n outpost-031-010-02-01 exec idler -- python /app/client.py tcp "$VISITOR_IP" 8080
kubectl -n outpost-031-010-02-01 exec idler -- python /app/client.py dns kubernetes.default.svc.cluster.local
```

The first command must print `open`. The next three must print `blocked`, and the last one `unresolved`.

`smith` reaches `forge` because both the egress rule on `smith` and the ingress rule on `forge` match. `smith` cannot reach `visitor`, because its egress rule names only `forge`. `visitor` times out because the ingress rule on `forge` names only `smith`.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> With only the ingress rule on `forge`, the request from `smith` still times out: the baseline isolates `smith` for egress.
>
> Do not give `default-deny-all` any rules, and do not narrow its `podSelector`. It must select every pod for both `Ingress` and `Egress`.
>
> Do not admit `smith` or `forge` by IP address with `ipBlock`, and do not add a `namespaceSelector` that matches another namespace. Select the pods by their label in `outpost-031-010-02-01`.
>
> Do not leave out `ports`, and do not add a rule with no peers, an empty peer or `namespaceSelector: {}`. Each of these opens far more than one path.
