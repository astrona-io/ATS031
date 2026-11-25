---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow A Pod Range With ipBlock And except Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-03-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-03-04" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

An `ipBlock` peer selects addresses by CIDR range instead of by labels. Its `except` list removes smaller ranges from it. Here the rule admits the pod range of the cluster but removes the address of the `rogue` pod with a `/32` entry, which is one single address.

Find the address of the `rogue` pod:

```sh
kubectl -n outpost-031-010-03-04 get pod rogue -o jsonpath='{.status.podIP}'
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

Then check the result. The test client prints `open` with the reply, or `blocked` when the connection times out:

```sh
LEDGER_IP=$(kubectl -n starfleet-031-010-03-04 get pod ledger -o jsonpath='{.status.podIP}')
kubectl -n outpost-031-010-03-04 exec courier -- python /app/client.py tcp "$LEDGER_IP" 7070
kubectl -n outpost-031-010-03-04 exec rogue -- python /app/client.py tcp "$LEDGER_IP" 7070
```

The request from `courier` must print `open` and the request from `rogue` must print `blocked`.

The `courier` pod gets a reply, because its address is inside the range and not in the `except` list. The `rogue` pod times out, because its `/32` address is removed. The `except` entry holds a pod address, so it stops matching if the `rogue` pod is recreated with a new address: this is why labels are the better tool for pods.

When you are done, remove the lab with `astrona destroy ats-031-lab-010-03-04`.

## Common pitfalls

> [!WARNING]
> Pod addresses change when a pod is recreated. Use `ipBlock` for stable ranges, such as addresses outside the cluster, and labels for pods.
>
> Every `except` range must be inside the `cidr` range, or the API server rejects the policy.
