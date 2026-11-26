# Allow A TCP Port Range And A Named UDP Port — Solution

You solve this lab with one NetworkPolicy. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the pod labels, the port names of the `meter` pod, and that no policy exists yet:

```sh
kubectl -n starfleet-031-010-03-05 get pods --show-labels
kubectl -n outpost-031-010-03-05 get pods --show-labels
kubectl -n starfleet-031-010-03-05 get pod meter -o jsonpath='{.spec.containers[0].ports}'
kubectl get networkpolicy -A
```

The `meter` pod names TCP port 7100 `admin` and UDP port 7200 `tick`. Without any policy, both `surveyor` and `loiterer` reach every port.

## Step 2: allow the TCP range (check `tcp-port-range`)

A port item can cover a range: `port` is the first port and `endPort` is the last one, both included. One item with `port: 7000` and `endPort: 7002` allows 7000, 7001 and 7002. The peer entry holds a `namespaceSelector` and a `podSelector` together, so only `surveyor` in `outpost-031-010-03-05` matches.

## Step 3: allow UDP by name (check `udp-named-port`)

A port item can also name a container port by the name in the pod spec instead of the number. `port: tick` with `protocol: UDP` matches UDP port 7200 in the `meter` pod. A rule with several port items allows any of them, so both items go into one rule.

Save this as `networkpolicy-meter-ports.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: meter-ports
  namespace: starfleet-031-010-03-05
spec:
  podSelector:
    matchLabels:
      app: meter
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: outpost-031-010-03-05
      podSelector:
        matchLabels:
          app: surveyor
    ports:
    - protocol: TCP
      port: 7000
      endPort: 7002
    - protocol: UDP
      port: tick
```

Apply it:

```sh
kubectl apply -f networkpolicy-meter-ports.yaml
```

TCP port 7100 is not in the list, so the `meter` pod no longer accepts it from anyone (check `admin-port-closed`).

## Step 4: test the ports (checks `tcp-port-range`, `udp-named-port` and `admin-port-closed`)

Every pod has a small test client. It prints `open` with the reply, or `blocked` when no reply comes within three seconds. Use `udp` instead of `tcp` for the UDP test:

```sh
METER_IP=$(kubectl -n starfleet-031-010-03-05 get pod meter -o jsonpath='{.status.podIP}')
kubectl -n outpost-031-010-03-05 exec surveyor -- python /app/client.py tcp "$METER_IP" 7000
kubectl -n outpost-031-010-03-05 exec surveyor -- python /app/client.py tcp "$METER_IP" 7002
kubectl -n outpost-031-010-03-05 exec loiterer -- python /app/client.py tcp "$METER_IP" 7001
```

The first two commands must print `open`. The last one must print `blocked`, because the peer entry selects only `surveyor`.

```sh
kubectl -n outpost-031-010-03-05 exec surveyor -- python /app/client.py udp "$METER_IP" 7200
kubectl -n outpost-031-010-03-05 exec surveyor -- python /app/client.py tcp "$METER_IP" 7100
kubectl -n outpost-031-010-03-05 exec loiterer -- python /app/client.py udp "$METER_IP" 7200
```

The first command must print `open`. UDP has no handshake, so a lost datagram can print `blocked` once; run it again before you change the policy. The other two must print `blocked`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Use exactly two port items: TCP `port: 7000` with `endPort: 7002`, and UDP `port: tick`. Three separate TCP items, or UDP `port: 7200` by number, do not pass.
>
> `endPort` needs a numeric `port`. A named port cannot start a range.
>
> Put the `namespaceSelector` and the `podSelector` in the same peer entry. Two entries are joined with OR and would let `loiterer` in.
>
> A named port matches the name in the selected pod. If the pod has no port with that name, the rule allows nothing.
