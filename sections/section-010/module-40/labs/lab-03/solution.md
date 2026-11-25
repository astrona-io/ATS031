---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow API Server Egress For One Pod Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-04-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-04-03" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

A pod reaches the API server through the `kubernetes` Service, but the network plugin sees the address and port behind it, after the Service translation. In kind these are the control plane node address and port 6443, not the Service address and port 443. The API server is not a pod with labels, so the rule uses an `ipBlock` with a `/32` range.

Find the address and port that the `kubernetes` Service sends requests to:

```sh
kubectl get endpointslice -n default -l kubernetes.io/service-name=kubernetes -o jsonpath='{.items[0].endpoints[0].addresses[0]} {.items[0].ports[0].port}'
```

Use the address in place of `<API_SERVER_IP>` and the port in place of `<API_SERVER_PORT>` in the file below.

Save this as `networkpolicy-operator-to-api-server.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: operator-to-api-server
  namespace: starfleet-031-010-04-03
spec:
  podSelector:
    matchLabels:
      app: operator
  policyTypes:
  - Egress
  egress:
  - to:
    - ipBlock:
        cidr: <API_SERVER_IP>/32
    ports:
    - protocol: TCP
      port: <API_SERVER_PORT>
```

Apply it:

```sh
kubectl apply -f networkpolicy-operator-to-api-server.yaml
```

Then check the result. The test client prints `open` with the last reply line, or `blocked` when the connection times out. Test the Service address, as a real client does:

```sh
API_SERVICE_IP=$(kubectl -n default get service kubernetes -o jsonpath='{.spec.clusterIP}')
kubectl -n starfleet-031-010-04-03 exec operator -- python /app/client.py tcp "$API_SERVICE_IP" 443
kubectl -n starfleet-031-010-04-03 exec helper -- python /app/client.py tcp "$API_SERVICE_IP" 443
```

The first command must print `open` and the second `blocked`.

The `operator` pod reaches the API server through the Service, because the rule allows the endpoint address and port. The `helper` pod still times out, because the policy selects only `operator`, and it still resolves names through `allow-dns`.

When you are done, remove the lab with `astrona destroy ats-031-lab-010-04-03`.

## Common pitfalls

> [!WARNING]
> A rule for port 443 does not work: the Service translates port 443 to the endpoint port before the policy check.
>
> The API server address can change when the control plane changes. Check the EndpointSlice again after a cluster rebuild.
