---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# ipBlock And Except

Some peers are not pods in the cluster. A database in a virtual network, a partner service or a corporate office has an IP address range, not a label. The `ipBlock` peer matches a source or destination by Classless Inter-Domain Routing (CIDR) range, which writes an address range as a base address and a prefix length such as `203.0.113.0/24`. This part explains `ipBlock` with its `except` list and demonstrates the mechanics with two pods.

## The fields

An `ipBlock` has a required `cidr` and an optional `except` list. The `except` entries must lie inside the `cidr`, and they remove addresses from the match. An `ipBlock` is its own peer type. It cannot share one entry with `podSelector` or `namespaceSelector`.

The Kubernetes documentation says to use `ipBlock` for addresses outside the cluster, because pod IP addresses are short-lived and change when a pod is replaced. Use it for pods only to understand the mechanics, as you do here.

## Mechanics with two pods

The example uses the address range `0.0.0.0/0`, which matches every IPv4 address, with the address of one pod removed. Two clients then differ only by their address. Start with no policy in `dock` and collect the addresses of two `shuttle` pods and of the `telemetry` pod:

<!-- astrona:playground:renew -->

```sh
kubectl -n dock delete networkpolicy --all
STARFLEET_SHUTTLE_IP=$(kubectl -n starfleet get pod shuttle -o jsonpath='{.status.podIP}')
OUTPOST_SHUTTLE_IP=$(kubectl -n outpost get pod shuttle -o jsonpath='{.status.podIP}')
TELEMETRY_IP=$(kubectl -n dock get pod telemetry -o jsonpath='{.status.podIP}')
echo "$STARFLEET_SHUTTLE_IP $OUTPOST_SHUTTLE_IP $TELEMETRY_IP"
```

The last command prints three different pod addresses. Save this as `networkpolicy-telemetry-ipblock.yaml`, and replace `<OUTPOST_SHUTTLE_IP>` with the value of `echo $OUTPOST_SHUTTLE_IP`, keeping the `/32` suffix that selects exactly one address:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: telemetry-ipblock
  namespace: dock
spec:
  podSelector:
    matchLabels:
      app: telemetry
  policyTypes:
  - Ingress
  ingress:
  - from:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - <OUTPOST_SHUTTLE_IP>/32
    ports:
    - protocol: TCP
      port: 9000
```

Apply it:

```sh
kubectl apply -f networkpolicy-telemetry-ipblock.yaml
```

Then check the result with `nc`, the netcat tool in the `busybox` image. The `telemetry` pod answers every connection on TCP port 9000 with one line of text. The request from `starfleet` should print that line. The request from `outpost` should print nothing and end after the three second limit, because its address is on the `except` list.

```sh
kubectl -n starfleet exec shuttle -- nc -w 3 "$TELEMETRY_IP" 9000
kubectl -n outpost exec shuttle -- nc -w 3 "$TELEMETRY_IP" 9000
```

The exact exit status of `nc` depends on its version, so judge the result by the text it prints. The network plugin matched the source address of each packet against the CIDR and the `except` entry. It made no use of labels at all.

## Pod IP addresses versus Service IP addresses

An `ipBlock` is compared with the real source or destination address of the packet. For traffic to a Service, the node rewrites the Service cluster IP address to a pod address before the policy rule is checked in most plugins, including Calico. A rule for a Service cluster IP address therefore does not match, and you must allow the pod addresses or select the pods by label.

For traffic from outside the cluster, the source address may also change on the way in, for example when a load balancer or a node masks it. An `ipBlock` for client addresses then sees the masked address. Check the behaviour of your plugin and cloud before you rely on it, and test with a real request.

## Node and pod ranges in kind

In a `kind` cluster the nodes are containers with addresses from a container network, and pods get addresses from a separate pod range. You can read the node addresses and the pod addresses with `kubectl get nodes -o wide` and `kubectl get pods -o wide`. An `ipBlock` for the pod range admits every pod, so it is as wide as a `namespaceSelector: {}`.

```sh
kubectl get nodes -o wide
kubectl -n dock delete networkpolicy telemetry-ipblock
```

You can now allow an address range and carve out one address, and you know the limits of the form. Ports are the second half of every rule, and the next part covers their forms.

## Common pitfalls

> [!WARNING]
> - **Putting `ipBlock` and a selector in one entry.** They are separate peer types; use separate entries.
> - **An `except` entry outside the `cidr`.** The API server rejects it.
> - **Using `ipBlock` for pods.** Pod addresses change when pods restart.
> - **Writing a rule for a Service IP address.** The plugin evaluates the pod address after translation.
