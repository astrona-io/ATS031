---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Block The Metadata Address For A Namespace Solution

## Inspect the starting state

Check that nothing restricts the pods yet. Define a function that prints the status code of a request to the metadata address, and send a request from `drifter`:

```sh
check_metadata() { kubectl -n "$1" exec "$2" -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/; }
kubectl get networkpolicy -A
check_metadata outpost drifter
```

The policy list is empty and the request prints `200`.

## Create the policy

The policy must select all pods with `podSelector: {}`, list `Egress` in `policyTypes`, and allow `0.0.0.0/0` with `169.254.169.254/32` in the `except` list. Because the rule allows every other address, DNS and both Services keep working without extra rules.

Save this as `networkpolicy-block-metadata.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-metadata
  namespace: outpost
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

Apply it:

```sh
kubectl apply -f networkpolicy-block-metadata.yaml
```

## Verify

Wait a few seconds, then check the blocked path, the two Services and the controls:

```sh
check_metadata outpost drifter
kubectl -n outpost exec drifter -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe/
kubectl -n outpost exec drifter -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe.starfleet.svc.cluster.local/
check_metadata starfleet shuttle
check_metadata metadata-stub control
```

The first request prints `000` and `kubectl` reports exit code 28. The two Service requests and the two control requests print `200`. If the first request still prints `200`, wait and run it again before you look for a mistake.
After recording your result, remove the independent lab with `astrona destroy ats-031-lab-040-02-01`.
