# Restrict A Pod To An Egress Allow-List — Solution

You solve this lab with one egress NetworkPolicy that selects `app: courier` and names the two destinations it needs. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

A blocked request proves nothing unless you know that the target answers. Store the pod IP addresses of the two web servers and send a request to each from `courier` and from `drifter`. The function `http_status` prints the HTTP status code of a request from a pod:

```sh
simulator_ip=$(kubectl -n starfleet-031-040-01-02 get pod metadata-simulator -o jsonpath='{.status.podIP}')
beacon_ip=$(kubectl -n outpost-031-040-01-02 get pod beacon -o jsonpath='{.status.podIP}')
http_status() { kubectl -n "$1" exec "$2" -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "$3"; }
http_status starfleet-031-040-01-02 courier "http://$simulator_ip:8080/"
http_status starfleet-031-040-01-02 courier "http://$beacon_ip:8080/"
http_status starfleet-031-040-01-02 courier http://probe/
http_status outpost-031-040-01-02 drifter "http://$simulator_ip:8080/"
kubectl -n starfleet-031-040-01-02 get networkpolicy
```

Every request prints `200`, and the namespace has no NetworkPolicy. Without a policy, `courier` can reach every pod in the cluster.

## Step 2: write the allow-list (check `metadata-blocked`)

An allow-list selects the pod for egress and names the destinations it needs. Everything else is blocked, including addresses you have not thought of. `courier` needs two destinations. The first is DNS, because it calls `probe` by name. The second is the `probe` pods on port 8080.

Save this as `networkpolicy-courier-egress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: courier-egress
  namespace: starfleet-031-040-01-02
spec:
  podSelector:
    matchLabels:
      app: courier
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
          app: probe
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-courier-egress.yaml
```

Wait a few seconds, then repeat the request to the simulator from both pods:

```sh
http_status starfleet-031-040-01-02 courier "http://$simulator_ip:8080/"
http_status outpost-031-040-01-02 drifter "http://$simulator_ip:8080/"
```

The request from `courier` prints `000`, and `kubectl` reports exit code 28, the `curl` time-out. The request from `drifter` prints `200`, which shows that the server still answers and that the `000` comes from the policy.

## Step 3: confirm the dependencies still work (check `dependencies-kept`)

The DNS rule lets `courier` resolve the name `probe`. The second rule names the pod port 8080, not the Service port 80: the network plugin checks the traffic after the Service address has been translated to a pod address. The policy selects by label, so a new pod with `app: courier` gets the same rules:

```sh
http_status starfleet-031-040-01-02 courier http://probe/
```

The request prints `200`, so DNS and the Service still work.

## Step 4: confirm nothing else is open (check `allow-list-only`)

`beacon` is not on the allow-list, so `courier` cannot reach it either. Pods without `app: courier` are not selected, so their egress does not change:

```sh
http_status starfleet-031-040-01-02 courier "http://$beacon_ip:8080/"
http_status outpost-031-040-01-02 drifter "http://$beacon_ip:8080/"
```

The request from `courier` prints `000`, and the request from `drifter` prints `200`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Without the DNS rule, the request to `http://probe/` fails, because `courier` cannot resolve the name. With port 80 instead of 8080 in the `probe` rule, the Service request also fails.
>
> A deny-list that excludes only the simulator address blocks it, but leaves `beacon` open. The checks reject any path from `courier` to `beacon`.
>
> Select the pods by `app: courier`, not every pod. The checks start a new pod with `app: courier`, which must follow the same rules, and a pod with another label, which must still reach `beacon`. Do not remove the label from `courier`.
