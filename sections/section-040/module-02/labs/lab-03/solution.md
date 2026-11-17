---
exam_objectives:
- Protect node metadata and endpoints
---
# Repair Metadata Policies That Do Not Block Solution

## Test before you read

A policy that exists is not proof that it works, so start with requests. Define two functions. The first prints the status code of a request to the metadata address, the second the status code of a request to the `probe` Service:

```sh
check_metadata() { kubectl -n "$1" exec "$2" -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/; }
check_probe() { kubectl -n "$1" exec "$2" -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe/; }
check_metadata starfleet-031-040-02-03 shuttle
check_metadata outpost-031-040-02-03 drifter
check_metadata dock-031-040-02-03 tender
check_probe dock-031-040-02-03 tender
```

The requests from `shuttle` and `drifter` print `200`: the address is open. The two requests from `tender` print `000`, and `kubectl` reports exit code 28, the `curl` time-out. The address is closed in `dock-031-040-02-03`, but so is the Service.

## Find the three mistakes

Now read the policies. The `-o yaml` output shows the full rule of each:

```sh
kubectl -n starfleet-031-040-02-03 get networkpolicy metadata-guard -o yaml
kubectl -n outpost-031-040-02-03 get networkpolicy metadata-guard -o yaml
kubectl -n dock-031-040-02-03 get networkpolicy metadata-guard -o yaml
```

Each policy selects all pods with `podSelector: {}`, so the selector is not the problem. The rules are:

- `starfleet-031-040-02-03` allows `0.0.0.0/0` with no `except` list. That range contains `169.254.169.254`, so the rule allows the address.
- `outpost-031-040-02-03` excludes `169.254.196.254/32`. The digits `169` and `196` are swapped, so the rule excludes an address that nobody uses and allows the real one.
- `dock-031-040-02-03` allows only port 53 to the cluster DNS pods. The pods can resolve the name `probe`, but the connection to the `probe` pod is not allowed, so the Service fails too.

## Repair the policies

The fix is the same for all three: allow all egress except the metadata address. A policy name is unique per namespace, so save one file per namespace. Save this as `networkpolicy-metadata-guard-starfleet.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: metadata-guard
  namespace: starfleet-031-040-02-03
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

Save this as `networkpolicy-metadata-guard-outpost.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: metadata-guard
  namespace: outpost-031-040-02-03
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

Save this as `networkpolicy-metadata-guard-dock.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: metadata-guard
  namespace: dock-031-040-02-03
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

Apply them. The command `kubectl replace` swaps the whole object, so no part of the old rule stays behind:

```sh
kubectl replace -f networkpolicy-metadata-guard-starfleet.yaml
kubectl replace -f networkpolicy-metadata-guard-outpost.yaml
kubectl replace -f networkpolicy-metadata-guard-dock.yaml
```

## Verify

Wait a few seconds, then repeat the tests for every client pod:

```sh
check_metadata starfleet-031-040-02-03 shuttle
check_metadata outpost-031-040-02-03 drifter
check_metadata dock-031-040-02-03 tender
check_probe starfleet-031-040-02-03 shuttle
check_probe outpost-031-040-02-03 drifter
check_probe dock-031-040-02-03 tender
check_metadata metadata-stub-031-040-02-03 control
```

The three metadata requests print `000`. The three Service requests and the request from `control` print `200`. The `200` from `control` shows that the metadata server still works, so the `000` comes from the policy. Then submit.

After recording your result, remove the independent lab with `astrona destroy ats-031-lab-040-02-03`.

## Common pitfalls

> [!WARNING]
> Check the `except` address digit by digit: a typo such as `169.254.196.254` is easy to miss and blocks nothing. A policy that allows only DNS does close the address, but it also closes every other destination. Always test a Service as well as the metadata address.
