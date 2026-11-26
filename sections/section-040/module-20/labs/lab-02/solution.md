# Allow The Metadata Address For One Labelled Pod — Solution

You solve this lab with two egress NetworkPolicies: one blocks the metadata address for every pod, and one allows it again for the label `role: cloud-agent`. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Both pods in `starfleet-031-040-02-02` can reach the address. Define a function that prints the status code of a request to the metadata address, and check them:

```sh
check_metadata() { kubectl -n "$1" exec "$2" -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/; }
kubectl -n starfleet-031-040-02-02 get pods --show-labels
check_metadata starfleet-031-040-02-02 agent
check_metadata starfleet-031-040-02-02 shuttle
```

Both requests print `200`.

## Step 2: block the address for every pod (check `shuttle-blocked`)

The first policy selects all pods with `podSelector: {}` and allows every address except the metadata address. Because the rule allows every other address, DNS and the `probe` Service keep working.

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

Apply it:

```sh
kubectl apply -f networkpolicy-block-metadata.yaml
```

Wait a few seconds, then check `shuttle`:

```sh
check_metadata starfleet-031-040-02-02 shuttle
kubectl -n starfleet-031-040-02-02 exec shuttle -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe/
```

The metadata request prints `000`, and `kubectl` reports exit code 28, the `curl` time-out. The Service request prints `200`. At this point `agent` is blocked as well.

## Step 3: allow the address for the label (check `agent-allowed`)

Policies add up. The second policy selects only pods with `role: cloud-agent` and allows the metadata address on port 80. A pod with the label is selected by both policies and gets the union of their rules: every address from the first, and the metadata address from the second.

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

Apply it:

```sh
kubectl apply -f networkpolicy-allow-metadata-agent.yaml
```

Wait a few seconds, then check `agent`:

```sh
check_metadata starfleet-031-040-02-02 agent
kubectl -n starfleet-031-040-02-02 exec agent -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe/
```

Both requests print `200`.

## Step 4: test new pods (check `label-decides`)

The label decides, not the pod name. Start one short-lived pod without labels and one with `role=cloud-agent`, and send the metadata request from each. The options `--rm` and `-i` attach to the pod and delete it when the command ends:

```sh
kubectl -n starfleet-031-040-02-02 run plain-check --rm -i --restart=Never --image=docker.io/curlimages/curl:8.11.1 --command -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/
kubectl -n starfleet-031-040-02-02 run agent-check --rm -i --restart=Never --labels=role=cloud-agent --image=docker.io/curlimages/curl:8.11.1 --command -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/
```

The first command prints `000`, and kubectl reports that the pod `terminated (Error)`, because `curl` exits with code 28 when its request times out. The second prints `200`. This also shows the risk of the design: anyone who can create a pod with that label in the namespace gets the address.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> A policy that selects `agent` by `app: agent`, or any policy that names one pod, gives the address to that pod only, and a new pod with `role: cloud-agent` stays blocked. A block policy that selects only `shuttle` leaves every new pod open.
>
> Do not let the exception policy be the only one that selects `agent`. Then `agent` can reach the metadata address and nothing else, and its request to `http://probe/` fails.
>
> Do not change the labels of `agent` or `shuttle`, and keep the policies in `starfleet-031-040-02-02`. The checks expect `drifter`, `tender` and `control` to still reach the metadata server.
