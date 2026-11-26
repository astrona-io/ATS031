# Allow DNS And One Application Dependency — Solution

You solve this lab with one NetworkPolicy. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the labels the policy will use, the Service port, and that no policy exists yet:

```sh
kubectl -n starfleet-031-010-01-02 get pods --show-labels
kubectl -n starfleet-031-010-01-02 get service archive
kubectl -n kube-system get pods -l k8s-app=kube-dns
kubectl get networkpolicy -A
```

The `archive` pods carry `app: archive` and the pod you must restrict carries `app: scanner`. The Service `archive` listens on port 80 and sends requests to the container port named `http`, which is TCP port 8080. CoreDNS, the cluster DNS server, runs in `kube-system` in pods with the label `k8s-app: kube-dns`.

## Step 2: allow DNS and the archive, nothing else (check `scanner-egress-policy`)

An egress policy controls the traffic that leaves a pod. Once a policy selects the `scanner` pod and lists `Egress` in `policyTypes`, the pod may only open connections that some egress rule allows. A pod that uses names also needs DNS, so the policy needs two rules: one to CoreDNS and one to the `archive` pods.

The DNS rule uses one peer entry with both a `namespaceSelector` and a `podSelector`. Together they mean "pods with the label `k8s-app: kube-dns` in the namespace `kube-system`". The label `kubernetes.io/metadata.name` is set by Kubernetes on every namespace and holds its name. DNS uses UDP port 53 for most queries and TCP port 53 for large answers, so the rule allows both.

The archive rule has only a `podSelector`, so it matches pods in the policy's own namespace. It uses TCP port 8080, the container port, not the Service port 80.

Save this as `networkpolicy-scanner-egress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: scanner-egress
  namespace: starfleet-031-010-01-02
spec:
  podSelector:
    matchLabels:
      app: scanner
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
          app: archive
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-scanner-egress.yaml
```

## Step 3: test the name and the Service (check `scanner-reaches-archive`)

Every pod has a small test client. It prints `open` with the reply, `blocked` when the connection times out, and `resolved` with the address or `unresolved` for a DNS lookup:

```sh
ARCHIVE_SERVICE_IP=$(kubectl -n starfleet-031-010-01-02 get service archive -o jsonpath='{.spec.clusterIP}')
echo "$ARCHIVE_SERVICE_IP"
kubectl -n starfleet-031-010-01-02 exec scanner -- python /app/client.py dns archive.starfleet-031-010-01-02.svc.cluster.local
kubectl -n starfleet-031-010-01-02 exec scanner -- python /app/client.py tcp "$ARCHIVE_SERVICE_IP" 80
```

The lookup must print `resolved` followed by the same address that `echo` printed. The request must print `open`.

The lookup works because the DNS rule matches the CoreDNS pods. The request to the Service on port 80 works because kube-proxy, the component that implements Services on each node, translates it to an `archive` pod on port 8080. The network plugin checks the connection after that translation, so the second rule allows it.

## Step 4: test the decoy (check `decoy-blocked`)

The `decoy` pod is a healthy listener on TCP port 8080. No rule allows it, so `scanner` must time out, while `idler`, which no policy selects, still reaches it:

```sh
DECOY_IP=$(kubectl -n starfleet-031-010-01-02 get pod decoy -o jsonpath='{.status.podIP}')
kubectl -n starfleet-031-010-01-02 exec scanner -- python /app/client.py tcp "$DECOY_IP" 8080
kubectl -n starfleet-031-010-01-02 exec idler -- python /app/client.py tcp "$DECOY_IP" 8080
```

The first command must print `blocked`. The second must print `open`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not write port 80 in the archive rule. The policy sees the pod port after the Service translation, so the rule must allow TCP 8080.
>
> Do not split the DNS peer into two entries, one with the `namespaceSelector` and one with the `podSelector`. Two entries are joined with OR, which allows every pod in `kube-system`, not only CoreDNS.
>
> Do not open more than you need: no rule without `ports`, no empty peer, no `namespaceSelector: {}`, no wide `ipBlock`, and only port 53 in the DNS rule. Select the `archive` pods by their label, not by address.
>
> Do not make the `podSelector` of the policy match `decoy`, `idler` or the `archive` pods. The policy must select only `scanner`.
