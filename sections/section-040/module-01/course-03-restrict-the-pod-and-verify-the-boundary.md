---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Restrict The Pod And Verify The Boundary

This part closes the path from `shuttle` to the stand-in endpoint with an egress allow-list, then proves three things with requests: the target still works, the restricted pod cannot reach it, and the dependencies the restricted pod needs still work. It ends with the provider-specific protections that a NetworkPolicy cannot replace.

## The allow-list policy

The policy selects `shuttle` for egress only. It allows DNS to CoreDNS, as the egress part of the first section explained, and TCP port 8080 to pods labelled `app: probe`. Nothing else is listed, so everything else is dropped, and that includes `metadata-simulator`, which is a pod with label `app: metadata-simulator`.

<!-- astrona:playground:renew -->

Save this as `networkpolicy-shuttle-isolation.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: shuttle-isolation
  namespace: starfleet
spec:
  podSelector:
    matchLabels:
      app: shuttle
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
    - port: 53
      protocol: UDP
    - port: 53
      protocol: TCP
  - to:
    - podSelector:
        matchLabels:
          app: probe
    ports:
    - port: 8080
      protocol: TCP
```

Apply it:

```sh
kubectl apply -f networkpolicy-shuttle-isolation.yaml
```

## Three checks

Run each check on its own. A request that is blocked ends with a nonzero exit status, so do not chain the commands with `&&` or run them under `set -e`.

```sh
SIM_IP=$(kubectl -n starfleet get pod metadata-simulator -o jsonpath='{.status.podIP}')
kubectl -n starfleet exec shuttle -- wget -q -T 3 -O- "http://$SIM_IP:8080/"
kubectl -n outpost exec drifter -- wget -q -T 3 -O- "http://$SIM_IP:8080/"
kubectl -n starfleet exec shuttle -- wget -q -T 3 -O- http://probe/
```

The first request, from `shuttle` to the stand-in, times out. The second, from `drifter`, still returns the directory listing. It proves that the stand-in is healthy, so the timeout in the first request comes from the policy and not from a broken server. The third request, from `shuttle` to the `probe` Service, returns the application response. It proves that DNS and the allowed dependency still work, even though the Service port is 80: the policy is evaluated after the Service address is translated to the pod, so the rule names the pod port 8080.

Together the three requests establish the boundary: the target works, the restricted source is blocked, and the permitted dependency survives. A single timeout alone would not tell you which of the three is true.

## Troubleshooting the result

If the first request still succeeds, check that the policy exists in the right namespace and that its `podSelector` matches the pod label with `kubectl -n starfleet get pod shuttle --show-labels`. Check also that the network plugin enforces policy. If every request from `shuttle` fails, including the third, the DNS rule or the `probe` rule is wrong. If `drifter` fails, the stand-in is not ready, or you used the wrong IP address. Delete a pod and recreate it and the IP changes, so read it again before each test.

## What the policy does not do

The policy has restricted one pod on the pod network. It has not changed the node, the metadata service or the credentials behind it. On a cloud cluster the following measures work together with a policy, and none replaces the others.

- **Restrict the path for all application pods.** Select the application namespaces with an egress policy that does not allow the metadata address, and treat the exceptions as reviewed.
- **Use the provider's protection for the metadata service.** Some providers require a session token for requests, limit the number of network hops a response may travel, or hide the node credentials from pods completely. These features reduce request forgery and accidental exposure. A compromised application that is still allowed to reach the service may be able to ask for a token, so they complement the network rule.
- **Give workloads their own identity.** Workload identity features of the provider issue narrow credentials to a ServiceAccount, so applications need nothing from the node.
- **Narrow the node identity.** Give the node role only what the node needs, so that exposure has a limited cost.
- **Close the other routes.** Keep anonymous kubelet access off, use Webhook authorization, never mount the runtime socket into application pods, and reject `hostNetwork` and `hostPath` for application namespaces with admission controls.

The playground proves only the network step. It does not prove that a real metadata service is protected. Report it that way.

## Clean up

Remove the policy and the stand-in if you want to repeat the exercise:

```sh
kubectl delete -f networkpolicy-shuttle-isolation.yaml
kubectl delete -f pod-metadata-simulator.yaml
```

## Common pitfalls

> [!WARNING]
> - **Calling a timeout proof.** Show that the target works from an unrestricted client.
> - **Forgetting DNS in the allow-list.** The restricted pod then fails on every name.
> - **Stopping at the network rule.** The credentials behind a real metadata service need their own limits.
> - **Using an old pod IP.** Read the address again after a pod is recreated.
