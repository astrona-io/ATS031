# Allow API Server Egress For One Pod — Solution

You solve this lab with one NetworkPolicy. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the pod labels and the two baseline policies:

```sh
kubectl -n starfleet-031-010-04-03 get pods --show-labels
kubectl -n starfleet-031-010-04-03 get networkpolicy -o yaml
```

`default-deny-all` selects every pod for ingress and egress. `allow-dns` lets every pod reach CoreDNS on port 53. Nothing allows a pod to reach the API server.

## Step 2: allow the API server endpoint (check `api-endpoint-rule`)

A pod reaches the API server through the `kubernetes` Service, but the network plugin checks the packet after the Service translation. It sees the endpoint address and port behind the Service, not the Service address and port 443. The API server is not a pod with labels, so the rule uses an `ipBlock`.

Read the endpoint address and port from the EndpointSlice of the `kubernetes` Service:

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

## Step 3: operator reaches the API server (check `operator-reaches-api`)

The `operator` pod sends its request to the Service address on port 443. kube-proxy translates it to the endpoint address and port, and the new rule allows that packet. Real clients use the Service address, so the test below does too.

## Step 4: keep the rule narrow (check `api-rule-narrow`)

The `/32` range is exactly one address, and the rule lists exactly one TCP port. The policy selects only `app: operator`, so `helper` keeps only what `allow-dns` gives it.

## Step 5: test allowed and blocked paths (checks `operator-reaches-api` and `api-rule-narrow`)

Every pod has a small test client. It prints `open` with the reply, `blocked` when the connection times out, and `resolved` or `unresolved` for a DNS lookup:

```sh
API_SERVICE_IP=$(kubectl -n default get service kubernetes -o jsonpath='{.spec.clusterIP}')
HELPER_IP=$(kubectl -n starfleet-031-010-04-03 get pod helper -o jsonpath='{.status.podIP}')
kubectl -n starfleet-031-010-04-03 exec operator -- python /app/client.py tcp "$API_SERVICE_IP" 443
kubectl -n starfleet-031-010-04-03 exec helper -- python /app/client.py tcp "$API_SERVICE_IP" 443
kubectl -n starfleet-031-010-04-03 exec operator -- python /app/client.py tcp "$HELPER_IP" 8080
kubectl -n starfleet-031-010-04-03 exec helper -- python /app/client.py dns kubernetes.default.svc.cluster.local
```

The first command must print `open`. The next two must print `blocked`. The last one must print `resolved`, because `allow-dns` still works for `helper`.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> A rule for the Service address or port 443 does not work: the Service translates the address and port to the endpoint before the policy check.
>
> Use exactly one `ipBlock` with the endpoint address and `/32`, and only the endpoint TCP port. A wider range, an extra peer or an extra port fails the check, and an `ipBlock` wider than `/16` or a rule without `ports` is always rejected.
>
> Do not change `default-deny-all` or `allow-dns`. A selector that also matches `helper` fails the check.
>
> The API server address can change when the control plane changes. Read the EndpointSlice again after a cluster rebuild.
