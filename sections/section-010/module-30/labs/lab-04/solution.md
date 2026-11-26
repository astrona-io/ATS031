# Allow A Pod Range With ipBlock And except — Solution

You solve this lab with one NetworkPolicy. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the pods, their addresses, and that no policy exists yet:

```sh
kubectl -n starfleet-031-010-03-04 get pods -o wide --show-labels
kubectl -n outpost-031-010-03-04 get pods -o wide --show-labels
kubectl get networkpolicy -A
```

The `ledger` pod listens on TCP 7070. The `courier` and `rogue` pods have addresses inside the pod range `192.168.0.0/16`. Without any policy, both can reach `ledger`.

## Step 2: allow the pod range (check `range-admits-courier`)

An `ipBlock` peer selects senders by address range in CIDR (Classless Inter-Domain Routing) notation instead of by labels. A `cidr` of `192.168.0.0/16` covers every pod address in this cluster, so the `courier` pod matches it.

## Step 3: remove the rogue address (checks `rogue-except-entry` and `range-admits-courier`)

The `except` list removes smaller ranges from the `cidr`. A `/32` entry is one single address. Find the address of the `rogue` pod:

```sh
ROGUE_IP=$(kubectl -n outpost-031-010-03-04 get pod rogue -o jsonpath='{.status.podIP}')
echo $ROGUE_IP
```

Use that address in place of `<ROGUE_IP>` in the file below.

Save this as `networkpolicy-ledger-from-pod-range.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ledger-from-pod-range
  namespace: starfleet-031-010-03-04
spec:
  podSelector:
    matchLabels:
      app: ledger
  policyTypes:
  - Ingress
  ingress:
  - from:
    - ipBlock:
        cidr: 192.168.0.0/16
        except:
        - <ROGUE_IP>/32
    ports:
    - protocol: TCP
      port: 7070
```

Apply it:

```sh
kubectl apply -f networkpolicy-ledger-from-pod-range.yaml
```

## Step 4: test both senders (checks `range-admits-courier` and `except-blocks-rogue`)

Every pod has a small test client. It prints `open` with the reply, or `blocked` when the connection times out:

```sh
LEDGER_IP=$(kubectl -n starfleet-031-010-03-04 get pod ledger -o jsonpath='{.status.podIP}')
kubectl -n outpost-031-010-03-04 exec courier -- python /app/client.py tcp "$LEDGER_IP" 7070
kubectl -n outpost-031-010-03-04 exec rogue -- python /app/client.py tcp "$LEDGER_IP" 7070
```

The first command must print `open`: the `courier` address is inside the range and not in the `except` list. The second must print `blocked`: the `rogue` address is removed.

The `except` entry holds a pod address, so it stops matching if the `rogue` pod is recreated with a new address. This is why labels are the better tool for pods.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> The `except` list must hold exactly one entry, the `rogue` address with `/32`. A wider entry, such as a `/24`, can also remove the `courier` address.
>
> Use only an `ipBlock` peer. Do not add a `podSelector` or a `namespaceSelector` to the rule.
>
> Use the `cidr` `192.168.0.0/16` and allow only TCP 7070. A rule without `ports` allows every port.
>
> Every `except` range must be inside the `cidr` range, or the API server rejects the policy.
