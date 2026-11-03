---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Policies On Services And Replicas

Clients call Services, but policies select pods. Pods come and go during rollouts and their labels can change. This part explains what the network plugin sees when a request goes through a Service, and shows that a policy follows labels and not pod identity, so it reacts when labels change and when pods are replaced.

## Policies do not know Services

A NetworkPolicy has no field for a Service. When `shuttle` calls the `probe` Service on port 80, the node rewrites the destination to the address of one `probe` pod and to port 8080. This rewrite is destination network address translation, done by `kube-proxy` rules on the node. The plugin then checks the policy against the pod address and the pod port. A rule for the Service port 80 never matches, and a rule for pod port 8080 does.

Start with a policy that allows `shuttle` in `starfleet` to reach the `probe` pods on port 80 by mistake. Because the pod listens on 8080, the Service request fails:

<!-- astrona:playground:renew -->

```sh
kubectl -n starfleet delete networkpolicy --all
```

Save this as `networkpolicy-probe-service-port.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: probe-from-shuttle
  namespace: starfleet
spec:
  podSelector:
    matchLabels:
      app: probe
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: shuttle
    ports:
    - protocol: TCP
      port: 80
```

Apply it and send a request through the Service:

```sh
kubectl apply -f networkpolicy-probe-service-port.yaml
kubectl -n starfleet exec shuttle -- wget -q -T 3 -O- http://probe/
```

The request times out. The rule names port 80, but the packet arrives at the pod on port 8080. Fix the policy by using the pod port. Save this as `networkpolicy-probe-pod-port.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: probe-from-shuttle
  namespace: starfleet
spec:
  podSelector:
    matchLabels:
      app: probe
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: shuttle
    ports:
    - protocol: TCP
      port: 8080
```

The policy name is unchanged, so applying the file replaces the old rule. Apply it and repeat the request:

```sh
kubectl apply -f networkpolicy-probe-pod-port.yaml
kubectl -n starfleet exec shuttle -- wget -q -T 3 -O- http://probe/
```

The request now returns the `probe` response.

## Label drift

A policy selects pods by their current labels, and the plugin re-evaluates it when labels change. Remove the allowed label from the client by changing it, and the access ends within seconds. Put it back, and the access returns.

```sh
kubectl -n starfleet label pod shuttle app=other --overwrite
kubectl -n starfleet exec shuttle -- wget -q -T 3 -O- http://probe/
kubectl -n starfleet label pod shuttle app=shuttle --overwrite
```

The request in the middle times out, because `app: other` does not match the peer. After you restore the label, the allowance applies again. This is why label permissions matter: anyone who can change a pod label can add or remove the pod from a policy. A short delay after a label change is normal while the plugin updates its rules, so repeat a request that fails right after the change.

## Replicas and rollouts

A policy applies to every pod that matches its selector, including pods that do not exist yet. When a Deployment creates new `probe` pods during a rollout, the new pods carry the label `app: probe` and are protected from the first moment. Restart the Deployment and request the Service again:

```sh
kubectl -n starfleet rollout restart deployment/probe
kubectl -n starfleet rollout status deployment/probe --timeout=120s
kubectl -n starfleet exec shuttle -- wget -q -T 3 -O- http://probe/
```

The request still works, and the denied path still holds for other clients. The policy did not need a change, because the new pods have new addresses but the same labels. Rules that depend on addresses, such as an `ipBlock` with a pod address, would break here, which is another reason to select pods by label.

You can now explain how a policy meets a Service, how a label change moves a pod in or out of a rule, and why rollouts need no policy change. These checks complete the set of peer and port forms.

```sh
kubectl -n starfleet delete networkpolicy probe-from-shuttle
```

## Common pitfalls

> [!WARNING]
> - **Writing the Service port.** Use the pod port that the container listens on.
> - **Relabelling a pod for debugging.** The change moves the pod out of every rule that depends on the label.
> - **Testing straight after a change.** Allow a few seconds, then repeat the request.
> - **Using pod addresses in rules.** Addresses change at every rollout; labels do not.
