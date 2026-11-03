---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Baselines Across Many Namespaces

A cluster has many namespaces, and a baseline in only one of them leaves the others open. NetworkPolicy is a namespaced object, so there is no single object that covers all namespaces. This part applies the same baseline to several namespaces with a label and a short shell loop, and previews each change with `kubectl diff` before it is applied.

## Label the namespaces you want to cover

A namespace label is a key and value pair on the Namespace object. You can select namespaces by label with `kubectl get namespaces -l` and use the result in a loop. Label `starfleet` and `dock` with a key that marks them as needing the baseline. Leave `outpost` out for now so that you can see the difference.

<!-- astrona:playground:renew -->

```sh
kubectl label namespace starfleet baseline=deny
kubectl label namespace dock baseline=deny
kubectl get namespaces -l baseline=deny
```

The listing shows the two labelled namespaces. The label has no effect on traffic. It only gives a loop something to select on.

## One file, applied per namespace

The baseline manifest has no `namespace` field, so the same file can be applied to any namespace with the `-n` flag. Save this as `networkpolicy-default-deny-all.yaml`:

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

Because the file has no namespace, `kubectl apply -f` without `-n` would use the namespace of the current context. Always pass `-n` explicitly in a loop.

## Preview with kubectl diff

`kubectl diff` sends the manifest to the API server in a dry-run mode and prints the difference between the live object and the file. It makes no change. For a new object it shows the whole object as added, and for an existing object it shows only the changed lines. Run it for each labelled namespace first:

```sh
for namespace in $(kubectl get namespaces -l baseline=deny -o jsonpath='{.items[*].metadata.name}'); do
  echo "namespace: $namespace"
  kubectl diff -n "$namespace" -f networkpolicy-default-deny-all.yaml
done
```

Each pass prints the policy that would be created. The command `kubectl diff` exits with status 1 when it finds a difference, so a shell with `set -e` stops at the first namespace. Do not treat that status as an error in this loop.

## Apply the same file to every labelled namespace

When the preview matches your intent, apply the file to each namespace in the same way:

```sh
for namespace in $(kubectl get namespaces -l baseline=deny -o jsonpath='{.items[*].metadata.name}'); do
  kubectl apply -n "$namespace" -f networkpolicy-default-deny-all.yaml
done
kubectl get networkpolicy --all-namespaces
```

The list shows `default-deny-all` in `starfleet` and `dock` and nothing in `outpost`. Prove the difference with requests. The `shuttle` pod in `outpost` has no policy on its side, but the `probe` pods in `starfleet` are isolated for ingress now:

```sh
kubectl -n outpost exec shuttle -- wget -q -T 3 -O- http://probe.starfleet/
```

The request times out. `outpost` has no baseline, which means its own pods are still open for any connection, including connections from `starfleet`. The unprotected namespace is the weak point of the set.

## Namespaces you create later

A label-driven loop covers the namespaces that exist when you run it. A namespace created afterwards has no policy. Kubernetes has no built-in way to apply a policy to every new namespace. Teams solve this with an admission policy or a controller that creates the baseline, or with a step in the namespace creation process. For the exam, remember that the baseline is per namespace and that you must repeat it for each namespace the task names.

You can now cover a set of namespaces from one manifest and preview each change first. The baseline gives the namespaces a safe start, and allow policies add the paths that the application needs.

## Common pitfalls

> [!WARNING]
> - **Leaving a namespace out.** A single namespace without a baseline is an open door into the others.
> - **Relying on the current context namespace.** Pass `-n` in every loop iteration.
> - **Treating `kubectl diff` exit status 1 as a failure.** It means a difference was found.
> - **Assuming new namespaces are covered.** The baseline applies only to namespaces that already have the policy.
