---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Selectors Recap And The Namespace Name Label

Every peer in a policy rests on a label selector, and a selector that does not match what you think it matches is the most common cause of a failed task. This part recaps how label selectors work, shows which labels a namespace has by default, and adds your own namespace labels so that you can see the difference between them.

## What a selector matches

A label selector is a list of conditions on labels. The simplest form is `matchLabels`, which lists key and value pairs, and an object matches when it has all of them. The second form is `matchExpressions`, which supports the operators `In`, `NotIn`, `Exists` and `DoesNotExist`. An empty selector `{}` matches every object in its scope.

A policy has three places where a selector appears. `spec.podSelector` chooses the pods the policy protects. A `podSelector` inside a peer chooses source or destination pods. A `namespaceSelector` inside a peer chooses whole namespaces. Each one reads the labels of a different object, so you must look at the right object.

## The automatic name label

Since Kubernetes 1.21 the API server sets the label `kubernetes.io/metadata.name` on every namespace. Its value is the name of the namespace. A user cannot set it to another name, which makes it the safest way to select a namespace by name.

<!-- astrona:playground:renew -->

```sh
kubectl get namespaces --show-labels
kubectl get namespace starfleet -o jsonpath='{.metadata.labels}'
```

The output shows `kubernetes.io/metadata.name` on `starfleet`, `outpost` and `dock`, next to the labels the cluster adds itself. There is no label such as `name: starfleet`. A policy that selects `name: starfleet` matches nothing, and that is a frequent error.

## Pod labels

The pods carry the labels that peers select on. List them in each namespace. The `shuttle` pods in all three namespaces have the same label, so a selector for `app: shuttle` alone cannot tell them apart.

```sh
kubectl get pods --all-namespaces --show-labels
```

This is the key observation for the rest of the module: two pods with the same labels in different namespaces differ only by their namespace. A rule must therefore name the namespace whenever the namespace matters.

## Labelling a namespace yourself

The automatic label selects one namespace by name. A label you add selects a group of namespaces. Label `starfleet` and `outpost` as members of the team `fleet`, and `dock` as a member of the team `logistics`:

```sh
kubectl label namespace starfleet team=fleet
kubectl label namespace outpost team=fleet
kubectl label namespace dock team=logistics
kubectl get namespaces -l team=fleet
```

The last command lists `starfleet` and `outpost`. A policy with `namespaceSelector: {matchLabels: {team: fleet}}` would match both. This is convenient, and it has a cost: anyone who can edit namespace labels can add a namespace to the group and gain the access. The automatic name label has no such weakness.

## Trust in labels

A selector trusts labels. Anyone who can create a pod in an allowed namespace can give that pod the allowed label, and anyone who can label a namespace can put it into an allowed group. Policy protects against pods that do not have the label, not against users who can set it. Keep the right to label namespaces and pods with the people who also own the policies.

You now know what each selector reads and which namespace labels exist. The next part uses them to allow a pod in another namespace.

## Common pitfalls

> [!WARNING]
> - **Selecting `name: starfleet`.** Namespaces have no `name` label by default. Use `kubernetes.io/metadata.name`.
> - **Reading the wrong object.** A `podSelector` reads pod labels, and a `namespaceSelector` reads namespace labels.
> - **Using a shared team label as a security boundary.** Anyone who can edit the label changes the result.
> - **Assuming equal pod labels mean one pod.** The same label in two namespaces matches both unless the namespace is named.
