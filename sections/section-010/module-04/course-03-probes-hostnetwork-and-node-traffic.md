---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Probes, hostNetwork And Node Traffic

A policy set can look complete and still leave traffic outside its reach. Some connections come from the node itself, and some pods share the network of the node and have no pod address of their own. This part shows what a NetworkPolicy applies to and what it does not, with the kubelet health probes and a `hostNetwork` pod as the two cases.

## Kubelet probes under a baseline

The kubelet is the agent on each node that starts pods and runs their health checks. A readiness or liveness probe of type HTTP is an HTTP request sent from the node to the pod. The `probe` pods use an HTTP readiness probe on port 8080, and the namespace has a default-deny policy, so the probe request would be dropped if policy applied to it.

<!-- astrona:playground:renew -->

```sh
kubectl -n starfleet get pods -o wide
kubectl -n starfleet get networkpolicy
```

The pods list shows the `probe` pods as ready even though `default-deny-all` isolates them for ingress. Calico lets a node reach the pods that run on it, so the probes pass. Not every network plugin behaves this way. If a plugin applies policy to node-to-pod traffic, probes fail under a baseline and pods never become ready, and then you must add a rule for the node address range. Check the plugin documentation and test with a baseline before you roll it out.

## hostNetwork pods

A pod with `hostNetwork: true` uses the network namespace of the node. It has no pod address of its own, and it listens on the node address. The `beacon` pod is such a pod. Read its address and compare it with a node address:

```sh
kubectl -n starfleet get pod beacon -o jsonpath='{.spec.hostNetwork}{"\n"}{.status.podIP}{"\n"}'
kubectl get nodes -o wide
```

The pod address printed by the first command is the address of the node that runs it. The Kubernetes documentation says that the behaviour of NetworkPolicy for `hostNetwork` pods is up to the network plugin. Calico does not apply pod policy to them, because they have no workload interface of their own, and it uses separate host endpoint policy for node traffic.

## See it with a request

The namespace `starfleet` is under a baseline, so a request from `outpost` to any normal pod in `starfleet` times out. Request the `beacon` pod from the unprotected `drifter` pod in `outpost`. The `beacon` pod serves a web page on port 9099.

```sh
BEACON_IP=$(kubectl -n starfleet get pod beacon -o jsonpath='{.status.podIP}')
kubectl -n outpost exec drifter -- wget -q -T 3 -O- "http://$BEACON_IP:9099/"
```

With Calico the request is expected to succeed even though the baseline selects every pod. If your result differs, record it and check how your plugin treats host-networked pods. The lesson holds either way: a baseline is not proof that every workload is closed.

## Writing a policy for the beacon

Try a policy that selects `beacon` and allows no ingress. If policy applied to the pod, the request above would stop. Save this as `networkpolicy-beacon-deny.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: beacon-deny
  namespace: starfleet
spec:
  podSelector:
    matchLabels:
      app: beacon
  policyTypes:
  - Ingress
```

Apply it and repeat the request:

```sh
kubectl apply -f networkpolicy-beacon-deny.yaml
kubectl -n outpost exec drifter -- wget -q -T 3 -O- "http://$BEACON_IP:9099/"
```

With Calico the request is expected to work as before, because the pod policy does not select the host-networked pod. Remove the policy with `kubectl -n starfleet delete networkpolicy beacon-deny` when you are done.

## What a NetworkPolicy does not cover

Four limits matter for the exam and for real clusters. First, it does not filter `hostNetwork` pods and node traffic in the way it filters pods. Second, it works on addresses, ports and protocols, so it cannot allow one HTTP path or method and deny another, which needs a service mesh or a gateway. Third, the core API has no logging or counters, so you cannot see which rule dropped a packet without plugin features. Fourth, it does not encrypt traffic or authenticate the peer; an allowed connection is a plain connection.

To protect node-level traffic, use the host firewall of the node or the host endpoint policy of the plugin. You now know what policy covers and where it stops. The next step is a method to prove the state of a policy set in a systematic way.

## Common pitfalls

> [!WARNING]
> - **Assuming a baseline covers every pod.** `hostNetwork` pods are outside pod policy in the plugin used here.
> - **Assuming probes always pass.** Some plugins apply policy to node traffic; test before a rollout.
> - **Expecting HTTP-level rules.** NetworkPolicy ends at address, port and protocol.
> - **Looking for drop logs in the API.** NetworkPolicy has no logging field.
