---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Block With An ipBlock Except Rule

The fastest way to close the metadata address for a whole namespace is one NetworkPolicy that allows all egress except that address. This part explains how the rule works, applies it to the `dock` namespace, and proves three things: the address is blocked, other egress still works, and the policy covers pods that did not exist when it was written.

## Why an except rule

Recall that a pod that no policy selects for egress can send traffic anywhere. The moment one policy selects it for egress, only the destinations that policies allow stay open. To block one address and keep everything else, the policy must select all pods and allow everything except that address. The field `ipBlock` describes a range of addresses in classless inter-domain routing (CIDR) notation, and its `except` list removes ranges from it. The range `0.0.0.0/0` means every IPv4 address, so `0.0.0.0/0` with the exception `169.254.169.254/32` means every address except the metadata address.

Three details decide whether the policy works:

- `podSelector: {}` selects every pod in the namespace of the policy, including pods created later.
- `policyTypes` should list `Egress` explicitly. If the field is missing, Kubernetes always assumes `Ingress` and adds `Egress` only when the policy has egress rules. Writing it out removes the guess.
- The `to` entry has only an `ipBlock`. An `ipBlock` cannot be combined with a `podSelector` or `namespaceSelector` in the same entry, and the API server rejects the policy if you try.

Because `0.0.0.0/0` includes the addresses of pods, Service traffic after it is translated to pod addresses, and the Domain Name System (DNS) server, the policy needs no separate rule for DNS or for in-cluster traffic. The Kubernetes documentation describes `ipBlock` as meant for addresses outside the cluster, and some network plugins treat pod addresses differently. Calico applies the range to any destination address, which is the behaviour this playground relies on.

## Apply the policy to dock

<!-- astrona:playground:renew -->

First record the baseline. The function sends one request to the metadata address and one to the `probe` Service in the same namespace:

```sh
check_metadata() { kubectl -n "$1" exec "$2" -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/; }
check_service() { kubectl -n "$1" exec "$2" -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe/; }
check_metadata dock tender
check_service dock tender
```

Both commands print `200`. Save this as `networkpolicy-block-metadata.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-metadata
  namespace: dock
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 169.254.169.254/32
```

Apply it:

```sh
kubectl apply -f networkpolicy-block-metadata.yaml
```

Then check the result with the same two functions:

```sh
check_metadata dock tender
check_service dock tender
```

Calico programs the rule within a moment, so if the first command still prints `200`, wait a few seconds and run it again. After that the first command prints `000` and exits with status 28, which is the `curl` exit code for a timeout, and `kubectl` reports that the command terminated with that exit code. The second command still prints `200`. The request to the `probe` Service needed a DNS lookup and a connection to a pod, and both stayed open.

## Prove other namespaces are unaffected

A policy lives in one namespace. Run the baseline function against a namespace that has no policy:

```sh
check_metadata outpost drifter
```

It prints `200`. This is the control request: it shows that the server is healthy and that the block in `dock` comes from the policy, not from a failure of the server.

You now know the deny-list form that blocks the address and keeps all other egress. Its weakness is the one you already know about deny-lists: it names only the address you thought of. It is still the right tool for this task, because the task names the address. The lab on the next page asks you to do this yourself in another namespace.

## Common pitfalls

> [!WARNING]
> - **Leaving out `policyTypes: [Egress]`.** It often works by inference, but a policy that lists only `Ingress` has no effect on egress.
> - **Using `/24` or another wide range in `except`.** Block exactly `169.254.169.254/32` unless the task says more.
> - **Putting `ipBlock` and a selector in the same `to` entry.** The API server rejects it. Use separate entries.
> - **Applying the policy in the wrong namespace.** A policy protects only pods in its own namespace.
> - **Testing too soon.** Wait a few seconds after `apply` before concluding the policy failed.
