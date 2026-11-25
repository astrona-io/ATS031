---
exam_objectives:
- Protect node metadata and endpoints
---
# Block The Metadata Address For A Namespace Solution

## Inspect the starting state

Check that nothing restricts the pods yet. Define a function that prints the status code of a request to the metadata address, and send a request from `drifter`:

```sh
check_metadata() { kubectl -n "$1" exec "$2" -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/; }
kubectl get networkpolicy -A
check_metadata outpost-031-040-02-01 drifter
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
  namespace: outpost-031-040-02-01
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
check_metadata outpost-031-040-02-01 drifter
kubectl -n outpost-031-040-02-01 exec drifter -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe/
kubectl -n outpost-031-040-02-01 exec drifter -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe.starfleet-031-040-02-01.svc.cluster.local/
check_metadata starfleet-031-040-02-01 shuttle
check_metadata metadata-stub-031-040-02-01 control
```

The first request prints `000` and `kubectl` reports exit code 28. The two Service requests and the two control requests print `200`. If the first request still prints `200`, wait and run it again before you look for a mistake.

The policy must also cover pods that start later. Start a short-lived pod with no special labels in the namespace and send the metadata request from it. The options `--rm` and `-i` attach to the pod and delete it when the command ends:

```sh
kubectl -n outpost-031-040-02-01 run meta-check --rm -i --restart=Never --image=docker.io/curlimages/curl:8.11.1 --command -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/
```

Next to a note about the command prompt and a line that says kubectl deleted the pod, the command prints `000`, because `podSelector: {}` selects the new pod as well. kubectl also reports that the pod `terminated (Error)`: `curl` exits with code 28 when its request times out. Then submit.

After recording your result, remove the independent lab with `astrona destroy ats-031-lab-040-02-01`.

## Common pitfalls

> [!WARNING]
> A policy with `podSelector` set to `app: drifter` blocks `drifter` and leaves every other pod in the namespace open. A policy that allows `0.0.0.0/0` without the `except` entry selects the pods and still allows the metadata address. Test from a new pod as well as from `drifter`.
