---
exam_objectives:
- Protect node metadata and endpoints
---
# Close Metadata Gaps Across Namespaces Solution

## Test coverage from new pods

An existing pod shows only how the policies treat that one pod. A new pod with no labels shows how they treat any workload that starts later. Define a function that starts such a pod in a namespace, sends one request to the metadata address and deletes the pod. The options `--rm` and `-i` attach to the pod and delete it when the command ends:

```sh
check_new_pod() { kubectl -n "$1" run "meta-check-$RANDOM" --rm -i --restart=Never --image=docker.io/curlimages/curl:8.11.1 --command -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/; }
for namespace in starfleet-031-040-02-04 outpost-031-040-02-04 dock-031-040-02-04; do
  echo "$namespace"
  check_new_pod "$namespace"
done
```

kubectl also prints a note about the command prompt and a line when it deletes each pod; the status code is the line on its own. The new pod in `starfleet-031-040-02-04` prints `000`, and kubectl adds that the pod `terminated (Error)`, because `curl` exits with code 28 when its request times out. The new pods in `outpost-031-040-02-04` and `dock-031-040-02-04` print `200`, so those two namespaces have a gap.

## Read the policies

List all policies with their pod selectors to see why:

```sh
kubectl get networkpolicy -A -o custom-columns=NAMESPACE:.metadata.namespace,NAME:.metadata.name,SELECTOR:.spec.podSelector
```

The policy in `outpost-031-040-02-04` selects only `app: drifter`, so every other pod is open. The namespace `dock-031-040-02-04` has no policy. The policy in `starfleet-031-040-02-04` selects all pods, which is right for `shuttle`, but it also blocks `agent`.

## Close the gaps

Use the same policy in both namespaces, with `podSelector: {}` so that it selects every pod. Save this as `networkpolicy-block-metadata-outpost.yaml`:

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

Save this as `networkpolicy-block-metadata-dock.yaml`:

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

Apply them. In `outpost-031-040-02-04` this updates the existing policy with the wider selector:

```sh
kubectl apply -f networkpolicy-block-metadata-outpost.yaml
kubectl apply -f networkpolicy-block-metadata-dock.yaml
```

## Add the exception

Keep the block in `starfleet-031-040-02-04` and add a second policy for the label. Policies add up, so a pod with `role=cloud-agent` gets the union of both rules: all egress except the address, plus the address on port 80. Save this as `networkpolicy-allow-metadata-agent.yaml`:

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

## Verify

Wait a few seconds, then repeat the coverage loop and check `agent`:

```sh
for namespace in starfleet-031-040-02-04 outpost-031-040-02-04 dock-031-040-02-04; do
  echo "$namespace"
  check_new_pod "$namespace"
done
kubectl -n starfleet-031-040-02-04 exec agent -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/
kubectl -n dock-031-040-02-04 exec tender -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe/
```

The three new pods print `000`. The request from `agent` and the Service request from `tender` print `200`. Then submit.

After recording your result, remove the independent lab with `astrona destroy ats-031-lab-040-02-04`.

## Common pitfalls

> [!WARNING]
> Deleting the block in `starfleet-031-040-02-04` gives `agent` the address, but it also opens the address for every other pod. Adding the exception to the block policy itself, with an `ipBlock` for the address, opens it for every pod as well, because the block selects all pods. Keep the block for all pods and put the exception in its own policy that selects the label.
