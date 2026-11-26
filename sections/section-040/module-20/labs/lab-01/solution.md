# Block The Metadata Address For A Namespace — Solution

You solve this lab with one egress NetworkPolicy that selects every pod in `outpost-031-040-02-01` and allows every address except the metadata address. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check that nothing restricts the pods yet. Define a function that prints the status code of a request to the metadata address, and send a request from `drifter`:

```sh
check_metadata() { kubectl -n "$1" exec "$2" -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/; }
kubectl get networkpolicy -A
check_metadata outpost-031-040-02-01 drifter
```

The policy list is empty and the request prints `200`.

## Step 2: create the policy (check `metadata-blocked`)

The policy must select all pods with `podSelector: {}`, list `Egress` in `policyTypes`, and allow `0.0.0.0/0` with `169.254.169.254/32` in the `except` list.

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

Wait a few seconds, then check the blocked path and the controls:

```sh
check_metadata outpost-031-040-02-01 drifter
check_metadata starfleet-031-040-02-01 shuttle
check_metadata metadata-stub-031-040-02-01 control
```

The first request prints `000`, and `kubectl` reports exit code 28, the `curl` time-out. The two control requests print `200`, because the policy exists only in `outpost-031-040-02-01`. If the first request still prints `200`, wait and run it again before you look for a mistake.

## Step 3: confirm the Services still work (check `services-kept`)

Because the rule allows every other address, DNS and both Services keep working without extra rules:

```sh
kubectl -n outpost-031-040-02-01 exec drifter -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe/
kubectl -n outpost-031-040-02-01 exec drifter -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe.starfleet-031-040-02-01.svc.cluster.local/
```

Both requests print `200`.

## Step 4: test a new pod (check `whole-namespace`)

The policy must also cover pods that start later. Start a short-lived pod with no special labels in the namespace and send the metadata request from it. The options `--rm` and `-i` attach to the pod and delete it when the command ends:

```sh
kubectl -n outpost-031-040-02-01 run meta-check --rm -i --restart=Never --image=docker.io/curlimages/curl:8.11.1 --command -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/
```

The command prints `000`, because `podSelector: {}` selects the new pod as well. kubectl also reports that the pod `terminated (Error)`: `curl` exits with code 28 when its request times out.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> A policy with `podSelector` set to `app: drifter` blocks `drifter` and leaves every other pod in the namespace open. The checks start a new pod without that label.
>
> A policy that allows `0.0.0.0/0` without the `except` entry selects the pods and still allows the metadata address. A policy whose rules do not allow CoreDNS breaks the requests by name, and the checks send both Service requests by name.
>
> Put the policy in `outpost-031-040-02-01` only. The checks expect `shuttle`, `agent`, `tender` and `control` to still reach the metadata server.
