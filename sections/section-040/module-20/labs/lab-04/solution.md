# Close Metadata Gaps Across Namespaces — Solution

You solve this lab by testing every namespace from a new pod, widening one policy, adding one missing policy and adding one exception policy. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

An existing pod shows only how the policies treat that one pod. A new pod with no labels shows how they treat any workload that starts later. Define a function that starts such a pod in a namespace, sends one request to the metadata address and deletes the pod. The options `--rm` and `-i` attach to the pod and delete it when the command ends:

```sh
check_new_pod() { kubectl -n "$1" run "meta-check-$RANDOM" --rm -i --restart=Never --image=docker.io/curlimages/curl:8.11.1 --command -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/; }
for namespace in starfleet-031-040-02-04 outpost-031-040-02-04 dock-031-040-02-04; do
  echo "$namespace"
  check_new_pod "$namespace"
done
```

The new pod in `starfleet-031-040-02-04` prints `000`, and kubectl adds that the pod `terminated (Error)`, because `curl` exits with code 28 when its request times out. The new pods in `outpost-031-040-02-04` and `dock-031-040-02-04` print `200`, so those two namespaces have a gap.

List all policies with their pod selectors to see why:

```sh
kubectl get networkpolicy -A -o custom-columns=NAMESPACE:.metadata.namespace,NAME:.metadata.name,SELECTOR:.spec.podSelector
```

The policy `block-metadata` in `outpost-031-040-02-04` selects only `app: drifter`, so every other pod is open. The namespace `dock-031-040-02-04` has no policy. The policy `block-metadata` in `starfleet-031-040-02-04` selects all pods, which is right for `shuttle`, but it also blocks `agent`.

## Step 2: widen the selector in outpost (check `outpost-covered`)

Use `podSelector: {}` so that the policy selects every pod, including pods that start later. The rule allows every address except the metadata address, so the `probe` Service keeps working.

Save this as `networkpolicy-block-metadata-outpost.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-metadata
  namespace: outpost-031-040-02-04
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

Apply it. This updates the existing policy with the wider selector:

```sh
kubectl apply -f networkpolicy-block-metadata-outpost.yaml
```

Wait a few seconds, then test a new pod again:

```sh
check_new_pod outpost-031-040-02-04
```

The command prints `000`.

## Step 3: add the missing policy in dock (check `dock-covered`)

The same policy closes the gap in `dock-031-040-02-04`. Save this as `networkpolicy-block-metadata-dock.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-metadata
  namespace: dock-031-040-02-04
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
kubectl apply -f networkpolicy-block-metadata-dock.yaml
```

Wait a few seconds, then test a new pod and the Service:

```sh
check_new_pod dock-031-040-02-04
kubectl -n dock-031-040-02-04 exec tender -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe/
```

The new pod prints `000`, and the Service request prints `200`.

## Step 4: add the exception in starfleet (check `agent-exception`)

Keep the block in `starfleet-031-040-02-04` and add a second policy for the label. Policies add up, so a pod with `role: cloud-agent` gets the union of both rules: all egress except the address, plus the address on port 80.

Save this as `networkpolicy-allow-metadata-agent.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-metadata-agent
  namespace: starfleet-031-040-02-04
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

Apply it:

```sh
kubectl apply -f networkpolicy-allow-metadata-agent.yaml
```

Wait a few seconds, then check `agent` and a new pod without the label:

```sh
kubectl -n starfleet-031-040-02-04 exec agent -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/
check_new_pod starfleet-031-040-02-04
```

The request from `agent` prints `200`, and the new pod prints `000`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Deleting the block in `starfleet-031-040-02-04` gives `agent` the address, but it also opens the address for `shuttle` and every new pod. Adding the exception to the block policy itself, with an `ipBlock` for the address, opens it for every pod as well, because the block selects all pods. Keep the block for all pods and put the exception in its own policy that selects the label.
>
> A policy that selects `app: drifter` covers only `drifter`. The checks start a new pod without labels in every namespace, and in `starfleet-031-040-02-04` also a pod with `role: cloud-agent`, which must reach the address.
>
> Do not add or remove labels on `agent` or `shuttle`, and do not touch `metadata-stub-031-040-02-04`: pod `control` must still reach the metadata server.
