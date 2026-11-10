---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Allow The Metadata Address For One Labelled Pod Solution

## Inspect the starting state

Both pods in `starfleet-031-040-02-02` can reach the address. Define the function and check them:

```sh
check_metadata() { kubectl -n "$1" exec "$2" -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/; }
kubectl -n starfleet-031-040-02-02 get pods --show-labels
check_metadata starfleet-031-040-02-02 agent
check_metadata starfleet-031-040-02-02 shuttle
```

Both requests print `200`.

## Block for everyone, allow for the label

Policies add up. The first policy selects all pods and allows everything except the metadata address. The second selects only pods with `role=cloud-agent` and allows the metadata address on port 80. A pod with the label is selected by both and gets the union.

Save this as `networkpolicy-block-metadata.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-metadata
  namespace: starfleet-031-040-02-02
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 169.254.169.254/32
```

Save this as `networkpolicy-allow-metadata-agent.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-metadata-agent
  namespace: starfleet-031-040-02-02
spec:
  podSelector:
    matchLabels:
      role: cloud-agent
  policyTypes:
  - Egress
  egress:
  - to:
    - ipBlock:
        cidr: 169.254.169.254/32
    ports:
    - protocol: TCP
      port: 80
```

Apply both files:

```sh
kubectl apply -f networkpolicy-block-metadata.yaml
kubectl apply -f networkpolicy-allow-metadata-agent.yaml
```

## Verify

Wait a few seconds, then run the checks:

```sh
check_metadata starfleet-031-040-02-02 agent
check_metadata starfleet-031-040-02-02 shuttle
kubectl -n starfleet-031-040-02-02 exec shuttle -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe/
kubectl -n starfleet-031-040-02-02 exec agent -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe/
check_metadata outpost-031-040-02-02 drifter
```

The request from `agent` prints `200`. The request from `shuttle` prints `000` with exit code 28. The two Service requests and the request from `drifter` print `200`. A common mistake is a second policy that selects `agent` but is the only one that selects it: then `agent` can reach the metadata address and nothing else, and the Service request fails.
After recording your result, remove the independent lab with `astrona destroy ats-031-lab-040-02-02`.
