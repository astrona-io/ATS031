---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Apply One Baseline To Labelled Namespaces Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-02-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-02-05" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

A NetworkPolicy is a namespaced object, so a baseline must exist in every namespace that needs it. A label on the namespaces lets you pick them with one selector, and one manifest without a `namespace` field can be applied to each of them with `kubectl -n`.

Label the two namespaces that must be restricted:

```sh
kubectl label namespace cargo-031-010-02-05 netpol=restricted
kubectl label namespace fuel-031-010-02-05 netpol=restricted
```

Write the baseline without a `namespace` field, so the same file fits every namespace.

Save this as `networkpolicy-default-deny-all.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

Apply it to every namespace with the label. The `for` loop reads the namespace names from the label selector:

```sh
for namespace in $(kubectl get namespaces -l netpol=restricted -o jsonpath='{.items[*].metadata.name}'); do
  kubectl -n "$namespace" apply -f networkpolicy-default-deny-all.yaml
done
```

Then check the result. List the labelled namespaces and the policies, then send one request into a labelled namespace. The test client prints `open` with the reply, or `blocked` when the connection times out:

```sh
kubectl get namespaces -l netpol=restricted
kubectl get networkpolicy --all-namespaces
LOADER_IP=$(kubectl -n cargo-031-010-02-05 get pod loader -o jsonpath='{.status.podIP}')
kubectl -n galley-031-010-02-05 exec cook -- python /app/client.py tcp "$LOADER_IP" 8080
```

The request from `cook` must print `blocked`.

Each labelled namespace now has its own `default-deny-all`, and the request into a labelled namespace times out. The `galley-031-010-02-05` namespace has no label, so the loop skipped it and it keeps no policy.

When you are done, remove the lab with `astrona destroy ats-031-lab-010-02-05`.

## Common pitfalls

> [!WARNING]
> A label on a namespace does nothing by itself. NetworkPolicy has no cluster-wide object; the label only helps you find the namespaces to apply the policy to.
>
> If the manifest has a `namespace` field, `kubectl -n` with a different namespace fails. Leave the field out of a shared baseline file.
