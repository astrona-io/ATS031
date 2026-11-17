---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Repair A Broken Policy Set Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-04-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-04-01" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

Repair a broken policy set one dependency at a time: test it, read the rule that should allow it, fix that rule, and test again. The `pathfinder` pod needs DNS, the `datastore` and the API server. Two faults block it.

First test DNS and the `datastore`:

```sh
kubectl -n starfleet-031-010-04-01 exec pathfinder -- python /app/client.py dns kubernetes.default.svc.cluster.local
kubectl -n starfleet-031-010-04-01 get networkpolicy pathfinder-egress datastore-ingress -o yaml
```

The DNS rule selects a namespace with the label `name: kube-system`, but namespaces carry `kubernetes.io/metadata.name: kube-system`, so the rule matches no namespace. It also allows only UDP port 53. The `datastore-ingress` policy lists `Egress` instead of `Ingress`, and its peer label `app: pathfindr` is misspelled, so the `datastore` pod stays closed under `default-deny-all`.

Find the API server address and port, because the repaired egress file keeps the API server rule:

```sh
kubectl get endpointslice -n default -l kubernetes.io/service-name=kubernetes -o jsonpath='{.items[0].endpoints[0].addresses[0]} {.items[0].ports[0].port}'
```

Use the address in place of `<API_SERVER_IP>` and the port in place of `<API_SERVER_PORT>` in the first file.

Save this as `networkpolicy-pathfinder-egress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: pathfinder-egress
  namespace: starfleet-031-010-04-01
spec:
  podSelector:
    matchLabels:
      app: pathfinder
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
  - to:
    - podSelector:
        matchLabels:
          app: datastore
    ports:
    - protocol: TCP
      port: 6379
  - to:
    - ipBlock:
        cidr: <API_SERVER_IP>/32
    ports:
    - protocol: TCP
      port: <API_SERVER_PORT>
```

Apply it:

```sh
kubectl apply -f networkpolicy-pathfinder-egress.yaml
```

Save this as `networkpolicy-datastore-ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: datastore-ingress
  namespace: starfleet-031-010-04-01
spec:
  podSelector:
    matchLabels:
      app: datastore
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: pathfinder
    ports:
    - protocol: TCP
      port: 6379
```

Apply it:

```sh
kubectl apply -f networkpolicy-datastore-ingress.yaml
```

Then check the result. The test client prints `open` with the reply, `blocked` when the connection times out, and `resolved` or `unresolved` for a DNS lookup:

```sh
DATASTORE_IP=$(kubectl -n starfleet-031-010-04-01 get pod datastore -o jsonpath='{.status.podIP}')
API_SERVICE_IP=$(kubectl -n default get service kubernetes -o jsonpath='{.spec.clusterIP}')
kubectl -n starfleet-031-010-04-01 exec pathfinder -- python /app/client.py dns kubernetes.default.svc.cluster.local
kubectl -n starfleet-031-010-04-01 exec pathfinder -- python /app/client.py tcp "$DATASTORE_IP" 6379
kubectl -n starfleet-031-010-04-01 exec pathfinder -- python /app/client.py tcp "$API_SERVICE_IP" 443
kubectl -n starfleet-031-010-04-01 exec stranger -- python /app/client.py tcp "$DATASTORE_IP" 6379
```

The lookup must print `resolved`. The next two commands must print `open`, and the last one `blocked`.

The lookup now succeeds, because the DNS rule matches CoreDNS on both protocols. The `pathfinder` pod reaches the `datastore`, because its egress rule and the repaired ingress rule both match. The `stranger` pod times out to the `datastore`, because the ingress rule names only `pathfinder`.

When you are done, remove the lab with `astrona destroy ats-031-lab-010-04-01`.

## Common pitfalls

> [!WARNING]
> A wrong label in a selector does not cause an error. The policy simply matches nothing; compare every selector with real labels.
>
> An ingress rule written under `egress` with `policyTypes: [Egress]` changes the wrong direction and can block the pod from sending.
