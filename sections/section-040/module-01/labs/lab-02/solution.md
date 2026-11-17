---
exam_objectives:
- Protect node metadata and endpoints
---
# Restrict A Pod To An Egress Allow-List Solution

## Record the baseline

A blocked request proves nothing unless you know that the target answers. Store the pod IP addresses of the two web servers and send a request to each from `courier` and from `drifter`. The function `check` prints the HTTP status code of a request from a pod:

```sh
SIM_IP=$(kubectl -n starfleet-031-040-01-02 get pod metadata-simulator -o jsonpath='{.status.podIP}')
BEACON_IP=$(kubectl -n outpost-031-040-01-02 get pod beacon -o jsonpath='{.status.podIP}')
check() { kubectl -n "$1" exec "$2" -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "$3"; }
check starfleet-031-040-01-02 courier "http://$SIM_IP:8080/"
check starfleet-031-040-01-02 courier "http://$BEACON_IP:8080/"
check starfleet-031-040-01-02 courier http://probe/
check outpost-031-040-01-02 drifter "http://$SIM_IP:8080/"
```

Every request prints `200`. Without a policy, `courier` can reach every pod in the cluster.

## Write the allow-list

An allow-list selects the pod for egress and names the destinations it needs. Everything else is blocked, including addresses you have not thought of. `courier` needs two destinations. The first is DNS, because it calls `probe` by name. The second is the `probe` pods on port 8080. The policy must name the pod port 8080, not the Service port 80: the network plugin checks the traffic after the Service address has been translated to a pod address.

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

## Verify

Wait a few seconds, then repeat the requests:

```sh
check starfleet-031-040-01-02 courier "http://$SIM_IP:8080/"
check starfleet-031-040-01-02 courier "http://$BEACON_IP:8080/"
check starfleet-031-040-01-02 courier http://probe/
check outpost-031-040-01-02 drifter "http://$SIM_IP:8080/"
check outpost-031-040-01-02 drifter "http://$BEACON_IP:8080/"
```

The first two requests print `000`, and `kubectl` reports exit code 28, the `curl` time-out. The request to `probe` prints `200`, so DNS and the Service still work. The two requests from `drifter` print `200`, which shows that both servers still answer and that the `000` comes from the policy. Then submit.

After recording your result, remove the independent lab with `astrona destroy ats-031-lab-040-01-02`.

## Common pitfalls

> [!WARNING]
> Without the DNS rule, the request to `http://probe/` fails, because `courier` cannot resolve the name. With port 80 instead of 8080 in the `probe` rule, the Service request also fails. A deny-list that excludes only the simulator address blocks it, but leaves `beacon` and every other address open.
