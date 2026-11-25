# Default Deny Plus A Selective Allow

Some pods have a real reason to read the metadata service. A cloud agent that manages volumes or load balancers, for example, may need the role of the node. A block for the whole namespace would break such a pod.

The safe design blocks the address for every pod and then opens it for the few pods that need it. On this page, you see how NetworkPolicy builds that design from rules that add up, and you apply it in the `dock` namespace. You also see why the label that opens the path must be protected.

## Policies add up

NetworkPolicy has no deny rule. A policy only lists what it allows. When several policies select the same pod for egress, the pod may send any traffic that one of them allows. The allowed traffic is the union of all the policies.

A selective allow uses this union. One policy allows everything except the metadata address, for all pods. A second policy allows the metadata address, for pods with one particular label. For a labelled pod, the union of the two policies covers every address. For every other pod, the union still leaves out the metadata address.

The label in this module is `role=cloud-agent`. The second policy selects pods by that label with `matchLabels`, and it allows egress to `169.254.169.254/32` on TCP port 80. Limiting the allow to that port is a good habit, because the metadata service uses only port 80.

![Diagram: a pod without the label is selected only by block-metadata and reaches every address except 169.254.169.254; a pod with role=cloud-agent is selected by block-metadata and allow-metadata-agent and reaches both other addresses and 169.254.169.254 port 80](images/two-policies-union.svg)

The drawing shows the two cases. A labelled pod matches both policies and gets the union of what they allow, so only that pod reaches the metadata address.

## Build the pair of policies

Now build the two policies in `dock`. The commands below need the `block-metadata` policy in `dock`, so you apply it again here. Applying an object that already exists with the same content changes nothing.

<!-- astrona:playground:renew -->

Save this as `networkpolicy-block-metadata.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-metadata
  namespace: dock
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

The second policy selects only pods with the label `role=cloud-agent` and allows them the metadata address on TCP port 80. Save this as `networkpolicy-allow-metadata-agent.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-metadata-agent
  namespace: dock
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

## Label a pod and watch the path open

The two policies are in place, but no pod in `dock` has the label yet. The pod `tender` has no `role` label, so only `block-metadata` selects it. Define the check function, and run it before and after you add the label:

```sh
check_metadata() { kubectl -n "$1" exec "$2" -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/; }
check_metadata dock tender
kubectl -n dock label pod tender role=cloud-agent
check_metadata dock tender
```

The first request prints `000`. After the label command, Calico sees the changed label and updates its rules for the pod, usually within a few seconds. The second request then prints `200`. If it still prints `000`, run it again.

The pod did not restart. Calico checks a policy selector against the current labels of the pod. So a label change moves the pod from one set of policies to another.

Now remove the label and check again. The minus sign at the end of the label name deletes the label:

```sh
kubectl -n dock label pod tender role-
check_metadata dock tender
```

The request prints `000` again, after the same short delay.

## Label discipline

The last test shows the weak point of the design. Whoever can change the labels of a pod can open the metadata path for it.

In role-based access control (RBAC) terms, the verbs `patch` and `update` on pods give this power. So does the permission to create pods with any labels: a team that can create pods in the namespace can create a pod with the `role=cloud-agent` label. Treat the label as a credential, and protect it in three ways:

- limit who can create pods in the namespace;
- use a label name that nobody can guess from the application;
- add an admission policy that rejects the label from anyone but the platform team. An admission policy is a rule that the API server checks when someone creates or changes an object.

An alternative design is a full default deny. One policy with `podSelector: {}` and an empty `egress` list blocks all egress. Further policies then allow DNS, the traffic inside the cluster and the agent's address. This design gives tighter control, but you must list every dependency of every pod, and a forgotten dependency breaks an application.

The pair of policies you built blocks one address and leaves the rest as it was. That is why it is the usual answer when a task asks only about the metadata address.

You now know how two policies add up to a block with one exception, and why the label behind the exception is a security control. The open question is how a policy that looks correct can still leave the address open.

## Common pitfalls

> [!WARNING]
> - **Writing the allow policy without the block policy.** A pod that only the allow policy selects can reach nothing except the metadata address.
> - **Matching the allow policy to the wrong labels.** The selector must match the labels on the pod itself, not the labels on the Deployment.
> - **Leaving the label unprotected.** Anyone who can create or patch pods can open the path.
> - **Allowing the whole `169.254.0.0/16` range.** The allow rule should name one address and one port.
