# Deny All Ingress In One Namespace — Solution

You solve this lab with one NetworkPolicy. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the pods in both namespaces, and that no policy exists yet:

```sh
kubectl -n dock-031-010-02-02 get pods --show-labels
kubectl -n outpost-031-010-02-02 get pods --show-labels
kubectl get networkpolicy -A
```

Each pod carries the label `app: <pod name>` and serves TCP port 8080. Without any policy, every pod can reach every other pod.

## Step 2: isolate every dock pod for ingress (check `ingress-denied`)

A default-deny ingress policy selects every pod in a namespace with `podSelector: {}` and lists only `Ingress` in `policyTypes`, with no `ingress` rules. A pod selected for ingress accepts only the traffic that some rule allows. This policy has no rules, so every pod in `dock-031-010-02-02` refuses all incoming connections.

Save this as `networkpolicy-default-deny-ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: dock-031-010-02-02
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

Apply it:

```sh
kubectl apply -f networkpolicy-default-deny-ingress.yaml
```

## Step 3: confirm traffic inside the namespace is blocked too (check `same-namespace-denied`)

The same policy covers this task. A NetworkPolicy does not trust pods because they share a namespace: once `vault` is selected for ingress, a request from `crane` needs a rule just like a request from `visitor`. No extra YAML is needed.

## Step 4: keep egress open (check `egress-still-open`)

The policy lists only `Ingress`, so it does not isolate the pods for egress. `crane` can still send requests to other pods, and `vault` can still reach CoreDNS, the cluster DNS server, to resolve names. Do not add `Egress` to `policyTypes` and do not create a second policy.

## Step 5: test blocked and open paths (all checks)

Every pod has a small test client. It prints `open` with the reply, `blocked` when the connection times out, and `resolved` or `unresolved` for a DNS lookup:

```sh
VAULT_IP=$(kubectl -n dock-031-010-02-02 get pod vault -o jsonpath='{.status.podIP}')
CRANE_IP=$(kubectl -n dock-031-010-02-02 get pod crane -o jsonpath='{.status.podIP}')
VISITOR_IP=$(kubectl -n outpost-031-010-02-02 get pod visitor -o jsonpath='{.status.podIP}')
kubectl -n outpost-031-010-02-02 exec visitor -- python /app/client.py tcp "$VAULT_IP" 8080
kubectl -n outpost-031-010-02-02 exec visitor -- python /app/client.py tcp "$CRANE_IP" 8080
kubectl -n dock-031-010-02-02 exec crane -- python /app/client.py tcp "$VAULT_IP" 8080
kubectl -n dock-031-010-02-02 exec vault -- python /app/client.py tcp "$CRANE_IP" 8080
```

All four commands must print `blocked`, also the two from the same namespace.

Now check that egress still works:

```sh
kubectl -n dock-031-010-02-02 exec crane -- python /app/client.py tcp "$VISITOR_IP" 8080
kubectl -n dock-031-010-02-02 exec vault -- python /app/client.py dns kubernetes.default.svc.cluster.local
```

The first command must print `open`, and the second must start with `resolved`.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not add `Egress` to `policyTypes`. With no egress rules, that blocks every outgoing connection, DNS included.
>
> Do not narrow `podSelector` to some pods, and do not add an `ingress` rule. The policy must select every pod and allow nothing in.
>
> Do not create a second policy in `dock-031-010-02-02` or any policy in `outpost-031-010-02-02`. The task allows only `default-deny-ingress`.
