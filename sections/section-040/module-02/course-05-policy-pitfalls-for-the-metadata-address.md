---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Policy Pitfalls For The Metadata Address

A NetworkPolicy that looks right can still leave the metadata address open. Most failures come from five patterns, and the exam rewards the learner who spots them quickly. This part walks through each pattern, runs the ones that are safe to run, and shows the one case where no pod policy helps at all.

## Pattern one: egress with no except entry

A policy that allows `0.0.0.0/0` without an `except` list selects the pods for egress and then allows every address, including the metadata address. It looks like a restriction because the file has an `egress` section, and it changes nothing. A request from a pod that this policy selects still succeeds. Always read the `except` list first when you review a policy for this task.

## Pattern two: a policy that allows only DNS

A policy with an egress rule for port 53 only blocks the metadata address, but it also blocks everything else. It is a restriction, so it does stop the metadata request. The application then fails because it cannot reach its own Services, and the usual reaction is to remove the policy. A correct task answer blocks the address and leaves the other egress open, or lists every dependency. Check the second half as carefully as the first.

## Pattern three: the policy is in the wrong namespace

A NetworkPolicy selects pods in its own namespace and nothing else. A policy in `starfleet` has no effect on pods in `outpost`. A copy of a file with the wrong `namespace` field, or an `apply` without `-n` on a file that has no namespace, makes this mistake. The cluster accepts the object and shows it in the list of policies, so the error is easy to miss.

## Pattern four: a wrong address or mask

`169.254.169.254/32` is exactly one address. A mask of `/24` covers 256 addresses, and a mask of `/16` covers the whole link-local range. A typo in one octet, such as `169.254.196.254`, blocks a different address and leaves the real one open. Type the address and the mask exactly as the task gives them, and read the stored object after you apply it.

## Pattern five: a pod on the host network

A pod that sets `hostNetwork: true` uses the network namespace of the node. It has no pod interface, and Calico does not apply pod NetworkPolicy to it. It reaches the metadata address no matter what policies exist in its namespace. This pattern needs no mistake in the policy at all. The remedy is to stop such pods from running in application namespaces, with an admission rule that rejects `hostNetwork`, and to review the ones that must run.

## See two patterns in the playground

<!-- astrona:playground:renew -->

Use the `outpost` namespace. First apply a correct blocking policy, so you have a protected state. Save this as `networkpolicy-block-metadata.yaml`:

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

Apply it and check the result from the client `drifter`:

```sh
kubectl apply -f networkpolicy-block-metadata.yaml
check_metadata() { kubectl -n "$1" exec "$2" -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/; }
check_metadata outpost drifter
```

After a few seconds the request prints `000`. Now start a pod that uses the host network in the same namespace. Save this as `pod-hostnet-client.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hostnet-client
  namespace: outpost
spec:
  hostNetwork: true
  restartPolicy: Never
  containers:
  - name: client
    image: docker.io/curlimages/curl:8.11.1
    command:
    - sleep
    - '3600'
```

Apply it, wait for it and send the same request from it:

```sh
kubectl apply -f pod-hostnet-client.yaml
kubectl -n outpost wait --for=condition=Ready pod/hostnet-client --timeout=120s
check_metadata outpost hostnet-client
```

The last command prints `200`. The policy `block-metadata` selects every pod in `outpost`, yet the pod `hostnet-client` reaches the address. The policy is correct, and the pod bypasses it because it does not use the pod network. Remove the test pod:

```sh
kubectl -n outpost delete pod hostnet-client
```

## How to review a policy quickly

When you read a policy for this task, ask these questions in order. Does the file select the pods that matter, in the right namespace? Does it list `Egress` in `policyTypes`? Is `169.254.169.254/32` in an `except` list, or absent from every allow rule? Does anything else that the pods need stay open? Could any pod in the namespace use the host network? Five questions take less than a minute and cover all five patterns.

You now know how a correct-looking policy fails. The last step is to check the whole cluster instead of one namespace at a time.

## Common pitfalls

> [!WARNING]
> - **Judging a policy by its file name or its `egress` section.** Read the `ipBlock` and its `except` list.
> - **Testing with a pod that is not selected.** Run the request from a pod the policy selects.
> - **Forgetting hostNetwork pods.** Pod policy does not apply to them. Find them with `kubectl get pods -A`.
> - **Trusting that an accepted object is correct.** The API server validates the format, not the intent.
