# Repair Metadata Policies That Do Not Block — Solution

You solve this lab by testing each namespace, finding the mistake in each `metadata-guard` policy and replacing all three with the same correct rule. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

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

Now read the policies. The `-o yaml` output shows the full rule of each:

```sh
kubectl -n starfleet-031-040-02-03 get networkpolicy metadata-guard -o yaml
kubectl -n outpost-031-040-02-03 get networkpolicy metadata-guard -o yaml
kubectl -n dock-031-040-02-03 get networkpolicy metadata-guard -o yaml
```

Each policy selects all pods with `podSelector: {}` and lists `Egress` in `policyTypes`, so the selector is not the problem. The mistakes are in the rules.

## Step 2: repair starfleet (check `starfleet-repaired`)

`metadata-guard` in `starfleet-031-040-02-03` allows `0.0.0.0/0` with no `except` list. That range contains `169.254.169.254`, so the rule allows the address. Add the `except` entry.

Save this as `networkpolicy-metadata-guard-starfleet.yaml`:

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

Apply it. The command `kubectl replace` swaps the whole object, so no part of the old rule stays behind:

```sh
kubectl replace -f networkpolicy-metadata-guard-starfleet.yaml
```

No other policy in the namespace allows the address, so `agent` and pods with `role: cloud-agent` are blocked as well. Wait a few seconds, then test:

```sh
check_metadata starfleet-031-040-02-03 shuttle
check_metadata starfleet-031-040-02-03 agent
check_probe starfleet-031-040-02-03 shuttle
```

The two metadata requests print `000`, and the Service request prints `200`.

## Step 3: repair outpost (check `outpost-repaired`)

`metadata-guard` in `outpost-031-040-02-03` excludes `169.254.196.254/32`. The digits `169` and `196` are swapped, so the rule excludes an address that nobody uses and allows the real one.

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

Apply it:

```sh
kubectl replace -f networkpolicy-metadata-guard-outpost.yaml
```

Wait a few seconds, then test:

```sh
check_metadata outpost-031-040-02-03 drifter
check_probe outpost-031-040-02-03 drifter
```

The metadata request prints `000`, and the Service request prints `200`.

## Step 4: repair dock (check `dock-repaired`)

`metadata-guard` in `dock-031-040-02-03` allows only port 53 to the cluster DNS pods. The pods can resolve the name `probe`, but the connection to the `probe` pod is not allowed, so the Service fails too. Replace the DNS-only rule with the same rule as in the other namespaces.

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

Apply it:

```sh
kubectl replace -f networkpolicy-metadata-guard-dock.yaml
```

Wait a few seconds, then test, and confirm that the metadata server itself still answers:

```sh
check_metadata dock-031-040-02-03 tender
check_probe dock-031-040-02-03 tender
check_metadata metadata-stub-031-040-02-03 control
```

The metadata request from `tender` prints `000`. The Service request and the request from `control` print `200`. The `200` from `control` shows that the metadata server still works, so the `000` comes from the policy.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Check the `except` address digit by digit: a typo such as `169.254.196.254` is easy to miss and blocks nothing.
>
> A policy that allows only DNS does close the address, but it also closes every other destination. The checks request `http://probe/` from every client, so test a Service as well as the metadata address.
>
> Keep `podSelector: {}`. The checks start new pods in every namespace, and in `starfleet-031-040-02-03` also a pod with `role: cloud-agent`; each one must be blocked from the metadata address.
