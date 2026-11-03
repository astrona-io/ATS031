---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# DNS And CoreDNS Egress

Almost every connection starts with a name lookup. When a namespace denies egress, the lookup is the first thing that stops, and every service that a pod calls by name appears to be down. This part shows the symptom on the `scout` pod, finds the DNS service, and writes the egress rule that restores resolution.

## The symptom

The `scout` pod runs a test script that does three independent things: it sends a DNS query, it calls the `probe` Service and it calls the Kubernetes API server. The script prints `ok` or `fail` for each step, and it uses a three second limit for each so it never hangs. Run it now:

<!-- astrona:playground:renew -->

```sh
kubectl -n starfleet exec scout -- python /app/check.py
```

The line must show `dns=fail`. Other steps may fail for other reasons, which later parts handle. The `default-deny-all` policy isolates every pod in `starfleet` for egress, and no rule yet allows the DNS query to leave the pod.

## Where DNS runs

CoreDNS is the DNS server of the cluster. It runs as pods in the `kube-system` namespace behind a Service named `kube-dns`. Pods learn its address from `/etc/resolv.conf`. A DNS query is an ordinary outgoing connection from the pod, so egress policy applies to it. Find the labels you can select on:

```sh
kubectl -n kube-system get pods -l k8s-app=kube-dns --show-labels
kubectl -n starfleet exec scout -- cat /etc/resolv.conf
kubectl get namespace kube-system --show-labels
```

The pods carry the label `k8s-app: kube-dns`. The namespace carries the automatic label `kubernetes.io/metadata.name: kube-system`. The `resolv.conf` file lists the cluster DNS Service address as the name server. The Service address is rewritten to a CoreDNS pod address before the policy is checked, so the rule selects the CoreDNS pods and not the Service address.

## Why both UDP and TCP

DNS normally uses UDP on port 53. When an answer is too large for one UDP message, or when the client chooses it, DNS falls back to TCP on port 53. A rule with only UDP works for most lookups and fails for large answers, which makes the fault intermittent and hard to find. Always allow both protocols.

## The egress rule

The rule needs one peer entry with two selectors in the same entry: the namespace by its automatic name label and the pods by `k8s-app: kube-dns`. Put them in one entry so that the rule means "CoreDNS pods in `kube-system`" and not "all pods in `kube-system` or any pod with that label in the policy namespace". Add the policy as a separate object that selects only `scout`. Policies add up, so it does not replace the existing ones.

Save this as `networkpolicy-scout-dns.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: scout-dns
  namespace: starfleet
spec:
  podSelector:
    matchLabels:
      app: scout
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
```

Apply it:

```sh
kubectl apply -f networkpolicy-scout-dns.yaml
```

Then check the result. The line must now show `dns=ok`. Other steps may still show `fail`.

```sh
kubectl -n starfleet exec scout -- python /app/check.py
```

## Common variations

Some clusters run a node-local DNS cache, and pods then send queries to an address on their own node instead of to CoreDNS pods. In that case the rule must allow that address. Read `/etc/resolv.conf` and the pods in `kube-system` to see which design your cluster uses, and test with a lookup rather than guess.

You can now restore name resolution under an egress baseline with one precise rule. The next question is what else a pod needs to leave the namespace for, starting with the API server.

## Common pitfalls

> [!WARNING]
> - **Allowing only UDP.** Large answers use TCP port 53.
> - **Selecting the whole `kube-system` namespace.** That opens every control plane add-on to the pod. Add the `k8s-app: kube-dns` pod selector in the same entry.
> - **Putting the selectors in two entries.** Two entries mean OR and widen the rule.
> - **Looking for the Service address.** The plugin matches the CoreDNS pod address after translation.
