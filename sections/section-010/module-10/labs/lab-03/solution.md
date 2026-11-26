# Isolate One Pod For Egress Only — Solution

You solve this lab with one NetworkPolicy. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the labels the policy will use, and that no policy exists yet:

```sh
kubectl -n starfleet-031-010-01-03 get pods --show-labels
kubectl -n starfleet-031-010-01-03 get networkpolicy
```

The pod you must isolate carries `app: relay`. The pods `lander` and `courier` carry `app: lander` and `app: courier`. Without any policy, every pod can reach every other pod.

## Step 2: isolate relay for egress only (check `relay-egress-policy`)

A pod is isolated for a direction when at least one policy selects it and lists that direction in `policyTypes`. Egress is the traffic a pod sends; ingress is the traffic it receives. A policy that lists only `Egress` and has no `egress` rules blocks every connection the pod opens, while incoming connections stay as they were.

Write `policyTypes` explicitly. If you leave it out, the API server fills it in from the rule sections you wrote. A policy with no rules would then get only `Ingress`, which is the opposite of what this task needs.

Save this as `networkpolicy-relay-egress-isolation.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: relay-egress-isolation
  namespace: starfleet-031-010-01-03
spec:
  podSelector:
    matchLabels:
      app: relay
  policyTypes:
  - Egress
```

Apply it:

```sh
kubectl apply -f networkpolicy-relay-egress-isolation.yaml
```

Then check that it is the only policy and lists only `Egress`:

```sh
kubectl -n starfleet-031-010-01-03 get networkpolicy
kubectl -n starfleet-031-010-01-03 get networkpolicy relay-egress-isolation -o jsonpath='{.spec.policyTypes}'
```

The second command must print `["Egress"]`.

## Step 3: test that relay cannot send (check `relay-egress-isolated`)

Every pod has a small test client. It prints `open` with the reply, `blocked` when the connection times out, and `resolved` or `unresolved` for a DNS lookup. Use the pod IP address of `lander`, so the TCP test does not depend on DNS:

```sh
LANDER_IP=$(kubectl -n starfleet-031-010-01-03 get pod lander -o jsonpath='{.status.podIP}')
kubectl -n starfleet-031-010-01-03 exec relay -- python /app/client.py tcp "$LANDER_IP" 8080
kubectl -n starfleet-031-010-01-03 exec relay -- python /app/client.py dns kubernetes.default.svc.cluster.local
```

The first command must print `blocked` and the second `unresolved`. The DNS lookup fails because a lookup is also a connection that `relay` opens, to CoreDNS, the cluster DNS server, and no egress rule allows it.

## Step 4: test that the other paths stay open (check `ingress-and-neighbours-open`)

The policy does not list `Ingress`, so other pods still reach `relay`. It does not select `lander` or `courier`, so nothing changes for them:

```sh
RELAY_IP=$(kubectl -n starfleet-031-010-01-03 get pod relay -o jsonpath='{.status.podIP}')
COURIER_IP=$(kubectl -n starfleet-031-010-01-03 get pod courier -o jsonpath='{.status.podIP}')
kubectl -n starfleet-031-010-01-03 exec courier -- python /app/client.py tcp "$RELAY_IP" 8080
kubectl -n starfleet-031-010-01-03 exec lander -- python /app/client.py tcp "$COURIER_IP" 8080
kubectl -n starfleet-031-010-01-03 exec lander -- python /app/client.py dns kubernetes.default.svc.cluster.local
```

The first two commands must print `open`. The last must print `resolved`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not leave out `policyTypes`. A policy without `policyTypes` and without rules isolates the pod for ingress only, so `relay` keeps sending.
>
> Do not list `Ingress` next to `Egress`. That also isolates `relay` for incoming traffic, and `courier` can no longer reach it.
>
> Do not add an egress rule, not even one for DNS. The task allows no egress at all, so a lookup that prints `unresolved` is expected and is not a CoreDNS fault.
>
> Do not use an empty `podSelector` or create a second policy. The policy must select only `relay`, and it must be the only policy in the namespace.
