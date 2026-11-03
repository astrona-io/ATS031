---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Deny All Egress And Its Side Effects

An egress baseline stops every pod in a namespace from opening outgoing connections. It limits what an attacker can do from a compromised pod, for example reach a database, an internal service or the internet. It is also the baseline that breaks things first, because every pod relies on outgoing connections that the application code never mentions. This part applies it to `dock`, shows the failure, and explains which component produced it.

## The policy

The egress baseline mirrors the ingress baseline. It selects all pods with `podSelector: {}`, lists `Egress` in `policyTypes` and has no `egress` section, so the list of allowed destinations is empty.

<!-- astrona:playground:renew -->

Save this as `networkpolicy-default-deny-egress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-egress
  namespace: dock
spec:
  podSelector: {}
  policyTypes:
  - Egress
```

Apply it:

```sh
kubectl apply -f networkpolicy-default-deny-egress.yaml
```

Then check the result. The `shuttle` pod in `dock` sends a request to the `probe` Service in `starfleet`, which has no policy. Egress of the sending pod is the only thing that changed.

```sh
kubectl -n dock exec shuttle -- wget -q -T 3 -O- http://probe.starfleet/
```

The request fails. The error is not a timeout of the connection to the `probe` pods. The error message says that `wget` could not resolve the address, or that the download timed out, depending on how the DNS lookup fails. Either way the request never reached `starfleet`.

## Why DNS breaks first

Before `wget` can open a connection to `probe.starfleet`, the pod must turn the name into an IP address. The pod sends a DNS query to the cluster DNS service on port 53. CoreDNS answers that query. CoreDNS runs as pods in the `kube-system` namespace, outside `dock`, so the query is an outgoing connection from the `shuttle` pod, and the egress baseline drops it.

Test this directly. The pod IP address of a `probe` pod in `starfleet` needs no DNS, so a request to the address shows whether the connection itself is blocked.

```sh
PROBE_IP=$(kubectl -n starfleet get pod -l app=probe -o jsonpath='{.items[0].status.podIP}')
kubectl -n dock exec shuttle -- wget -q -T 3 -O- "http://$PROBE_IP:8080/"
```

This request also fails, with a timeout, because the egress baseline blocks every outgoing connection and not only DNS. Two separate things are now blocked: name resolution and the application connection. When you open one path, test both.

## Other traffic that stops

Egress policy applies to everything a pod sends. Four categories fail in a namespace with this baseline:

- DNS queries to CoreDNS (UDP and TCP port 53).
- Connections to other pods and Services.
- Connections to the Kubernetes API server, for pods that call the API with their ServiceAccount.
- Connections to anything outside the cluster, such as a package mirror or a database.

The probes of the kubelet (the node agent) are different. The kubelet sends readiness and liveness probes from the node, and the pods still show as ready. The plugin treats traffic from a node to its own pods separately from pod egress, and Calico allows it by default.

```sh
kubectl -n dock get pods
```

Both `probe` pods and the `shuttle` pod stay in the `Running` state. A pod does not fail when its egress is blocked unless the application exits on an error. The failure is visible in the requests, not in the pod status, which is why the baseline is easy to apply and hard to debug.

## Seeing which side drops the packet

A blocked egress request and a blocked ingress request look the same to the client: a timeout. The policy list tells you which side to look at. For a request from `dock` to `starfleet`, check `dock` for egress policies and `starfleet` for ingress policies:

```sh
kubectl get networkpolicy --all-namespaces
```

Only `default-deny-egress` in `dock` exists, so the egress side is the cause. A connection needs permission on both sides wherever both sides are isolated. The source namespace must allow the egress, and the destination namespace must allow the ingress.

You can now apply an egress baseline and recognise its first side effect, DNS. The next part adds allow rules on top of baselines and fixes the DNS failure in an order that does not lock you out.

## Common pitfalls

> [!WARNING]
> - **Blaming the destination.** With an egress baseline the source namespace causes the drop. Check the policies of the source first.
> - **Testing a Service name after denying egress.** The name lookup fails before any connection is made. Test with a pod IP address to separate DNS from the connection.
> - **Expecting a pod status change.** Blocked egress does not stop a pod. Only requests fail.
> - **Forgetting the API server.** Pods that call the Kubernetes API need an egress rule for it.
