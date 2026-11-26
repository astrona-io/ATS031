# Deny All Egress And Observe DNS Fail — Solution

You solve this lab with one NetworkPolicy. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the pods in both namespaces, and that no policy exists yet:

```sh
kubectl -n dock-031-010-02-03 get pods --show-labels
kubectl -n outpost-031-010-02-03 get pods --show-labels
kubectl get networkpolicy -A
```

Each pod carries the label `app: <pod name>` and serves TCP port 8080. Without any policy, every pod can reach every other pod.

## Step 2: isolate every dock pod for egress (check `egress-denied`)

A default-deny egress policy selects every pod in a namespace with `podSelector: {}` and lists only `Egress` in `policyTypes`, with no `egress` rules. A pod selected for egress may open only the connections that some rule allows. This policy has no rules, so the pods in `dock-031-010-02-03` cannot open any outgoing connection, also not to each other.

Save this as `networkpolicy-default-deny-egress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-egress
  namespace: dock-031-010-02-03
spec:
  podSelector: {}
  policyTypes:
  - Egress
```

Apply it:

```sh
kubectl apply -f networkpolicy-default-deny-egress.yaml
```

## Step 3: see DNS fail (check `dns-denied`)

The same policy covers this task. A DNS lookup is an outgoing connection from the pod to CoreDNS, the cluster DNS server, on port 53. With no egress rule, the lookup times out, so the pod can no longer turn a name into an address. No extra YAML is needed.

## Step 4: keep ingress open (check `ingress-still-open`)

The policy lists only `Egress`, so it does not isolate the pods for ingress. `pilot` can still open a connection to `hauler` and `winch`. The reply from `hauler` is not new egress: the network plugin tracks the connection and lets the reply through. Do not add `Ingress` to `policyTypes` and do not create a second policy.

## Step 5: test blocked and open paths (all checks)

Every pod has a small test client. It prints `open` with the reply, `blocked` when the connection times out, and `resolved` or `unresolved` for a DNS lookup:

```sh
PILOT_IP=$(kubectl -n outpost-031-010-02-03 get pod pilot -o jsonpath='{.status.podIP}')
HAULER_IP=$(kubectl -n dock-031-010-02-03 get pod hauler -o jsonpath='{.status.podIP}')
WINCH_IP=$(kubectl -n dock-031-010-02-03 get pod winch -o jsonpath='{.status.podIP}')
kubectl -n dock-031-010-02-03 exec hauler -- python /app/client.py tcp "$PILOT_IP" 8080
kubectl -n dock-031-010-02-03 exec hauler -- python /app/client.py tcp "$WINCH_IP" 8080
kubectl -n dock-031-010-02-03 exec winch -- python /app/client.py dns kubernetes.default.svc.cluster.local
```

The first two commands must print `blocked` and the third `unresolved`.

Now check that ingress still works:

```sh
kubectl -n outpost-031-010-02-03 exec pilot -- python /app/client.py tcp "$HAULER_IP" 8080
kubectl -n outpost-031-010-02-03 exec pilot -- python /app/client.py tcp "$WINCH_IP" 8080
```

Both must print `open`.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not add `Ingress` to `policyTypes`. With no ingress rules, that blocks `pilot` from reaching the dock pods.
>
> Do not narrow `podSelector` to some pods, and do not add an `egress` rule, not even one for DNS. The task asks for no egress at all.
>
> Do not create a second policy in `dock-031-010-02-03` or any policy in `outpost-031-010-02-03`. The task allows only `default-deny-egress`.
>
> In real work, DNS is usually the first thing that breaks after an egress baseline. Add a DNS rule first when the pods use names.
