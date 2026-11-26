# Repair A Broken Policy Set — Solution

You solve this lab by repairing two NetworkPolicies. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Read the three policies and the labels they must match:

```sh
kubectl -n starfleet-031-010-04-01 get pods --show-labels
kubectl -n starfleet-031-010-04-01 get networkpolicy
kubectl -n starfleet-031-010-04-01 get networkpolicy pathfinder-egress datastore-ingress -o yaml
kubectl get namespace kube-system --show-labels
```

`default-deny-all` selects every pod for ingress and egress, so a pod can send or receive only what another policy allows. It is correct and stays as it is.

The DNS rule in `pathfinder-egress` selects a namespace with the label `name: kube-system`. Namespaces carry `kubernetes.io/metadata.name: kube-system`, so the rule matches no namespace, and it allows only UDP port 53. The `datastore-ingress` policy lists `Egress` instead of `Ingress`, and its peer label `app: pathfindr` is misspelled, so the `datastore` pod accepts no connection.

## Step 2: repair the DNS rule (check `dns-egress`)

The repaired rule selects the CoreDNS pods with one peer entry: a `namespaceSelector` on the automatic name label and a `podSelector` on `k8s-app: kube-dns`. Both selectors in one entry must match, so the rule reaches only CoreDNS. It lists UDP and TCP port 53, because a DNS client switches to TCP when an answer is too large for UDP.

The rest of the file stays as it is: the `datastore` rule and the API server rule. The API server rule needs the real address and port of the API server. Read them from the EndpointSlice of the `kubernetes` Service:

```sh
kubectl get endpointslice -n default -l kubernetes.io/service-name=kubernetes -o jsonpath='{.items[0].endpoints[0].addresses[0]} {.items[0].ports[0].port}'
```

Use the address in place of `<API_SERVER_IP>` and the port in place of `<API_SERVER_PORT>` in the file below.

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

## Step 3: keep the other dependencies of pathfinder (check `pathfinder-dependencies`)

The `pathfinder` pod already has egress rules for the `datastore` and for the API server. The API server rule names the endpoint address with a `/32` range, because the network plugin checks the packet after the Service has translated the address and port 443 to the endpoint.

The `datastore` connection still fails after Step 2. Egress from `pathfinder` is allowed, but ingress to the `datastore` is not, and a connection needs both. Step 4 repairs the ingress side, and this check passes with it.

## Step 4: repair the datastore ingress policy (check `datastore-ingress`)

The policy must list `Ingress` in `policyTypes` and keep its rule under `ingress`, with a `from` peer that selects `app: pathfinder`. A `from` entry with only a `podSelector` matches pods in the policy's own namespace, so `stranger` stays out.

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

`kubectl apply` replaces the whole spec, so the old `egress` rule and the `Egress` policy type are gone.

## Step 5: test every dependency (checks `dns-egress`, `pathfinder-dependencies` and `datastore-ingress`)

Every pod has a small test client. It prints `open` with the reply, `blocked` when the connection times out, and `resolved` or `unresolved` for a DNS lookup:

```sh
DATASTORE_IP=$(kubectl -n starfleet-031-010-04-01 get pod datastore -o jsonpath='{.status.podIP}')
STRANGER_IP=$(kubectl -n starfleet-031-010-04-01 get pod stranger -o jsonpath='{.status.podIP}')
API_SERVICE_IP=$(kubectl -n default get service kubernetes -o jsonpath='{.spec.clusterIP}')
kubectl -n starfleet-031-010-04-01 exec pathfinder -- python /app/client.py dns kubernetes.default.svc.cluster.local
kubectl -n starfleet-031-010-04-01 exec pathfinder -- python /app/client.py tcp "$DATASTORE_IP" 6379
kubectl -n starfleet-031-010-04-01 exec pathfinder -- python /app/client.py tcp "$API_SERVICE_IP" 443
kubectl -n starfleet-031-010-04-01 exec pathfinder -- python /app/client.py tcp "$STRANGER_IP" 8080
kubectl -n starfleet-031-010-04-01 exec stranger -- python /app/client.py tcp "$DATASTORE_IP" 6379
```

The lookup must print `resolved`. The next two commands must print `open`, and the last two `blocked`.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not change or delete `default-deny-all`. The checks require it to select every pod for ingress and egress with no rules.
>
> Allow both UDP and TCP port 53, and select CoreDNS with the `kubernetes.io/metadata.name: kube-system` namespace label and `k8s-app: kube-dns` in one peer entry. A rule that only fixes the label but keeps UDP alone does not pass.
>
> Do not widen any rule to make traffic flow. A rule without `to` or `from`, an empty peer, `namespaceSelector: {}`, an `ipBlock` wider than `/16` or a rule without `ports` fails the check. Keep the API server rule at one `/32` address.
>
> Admit `pathfinder` to the `datastore` by its label, not with an `ipBlock`, and allow only TCP port 6379. A selector that also matches `stranger` fails the check.
