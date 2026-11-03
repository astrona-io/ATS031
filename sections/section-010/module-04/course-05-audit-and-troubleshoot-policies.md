---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Audit And Troubleshoot Policies

When a request fails or succeeds unexpectedly, guessing wastes time. A fixed method finds the cause in a few commands: list the policies, read what each one selects, compare selectors with real labels, check the policy types, and confirm that the plugin enforces policy. This part lists the policies of the `starfleet` namespace, finds the faults that still break the `probe` step of `scout`, and repairs them.

## Step one: list and read

List every policy in the cluster, then describe the ones in `starfleet`. The listing shows the name and the pod selector of each policy. The `describe` output shows what each policy allows.

<!-- astrona:playground:renew -->

```sh
kubectl get networkpolicy --all-namespaces
kubectl -n starfleet describe networkpolicy scout-to-probe
kubectl -n starfleet describe networkpolicy probe-ingress
```

The `scout-to-probe` policy allows egress from `scout` to pods labelled `app: probe` in a namespace selected by a label. The `probe-ingress` policy selects the `probe` pods. Read the type line of each: one of them reports an egress rule where an ingress rule is needed.

## Step two: compare selectors with real labels

A selector that matches nothing is valid, and the policy then protects or allows nothing. Compare the labels in the policies with the labels in the cluster.

```sh
kubectl get namespace starfleet --show-labels
kubectl -n starfleet get pods --show-labels
```

The namespace has `kubernetes.io/metadata.name: starfleet` and no `name` label, so a namespace selector on `name` matches nothing. The `scout` pod carries `app: scout`, and a peer that selects any other value for the app label matches no pod.

## Step three: policy types and direction

A policy affects the directions in its `policyTypes`. A policy for `probe` that lists `Egress` and has an `egress` section controls what the `probe` pods send. It adds nothing for what they receive, so the ingress side stays closed by the baseline. Check that the type matches the direction of the traffic you want to allow, and that the rules sit under the matching section.

## Step four: the plugin

Policies have an effect only if the network plugin enforces them. The `kind` default plugin does not. Confirm which plugin runs, and test a deny:

```sh
kubectl -n kube-system get pods -o wide
```

The list contains the Calico pods. If a cluster has only a plugin without policy support, objects are accepted and nothing is blocked, and no `kubectl` command reports it. A deny test that fails to deny is the signal.

## Repair

The faults are now known: the probe rule in `scout-to-probe` selects the namespace by a label that does not exist, the `probe-ingress` policy has the wrong direction, and its peer selects a mistyped pod label. Replace the first policy with the correct label. Save this as `networkpolicy-scout-to-probe.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: scout-to-probe
  namespace: starfleet
spec:
  podSelector:
    matchLabels:
      app: scout
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: starfleet
      podSelector:
        matchLabels:
          app: probe
    ports:
    - protocol: TCP
      port: 8080
```

Then save the corrected ingress policy as `networkpolicy-probe-ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: probe-ingress
  namespace: starfleet
spec:
  podSelector:
    matchLabels:
      app: probe
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: scout
    ports:
    - protocol: TCP
      port: 8080
```

Apply both files and run the script again:

```sh
kubectl apply -f networkpolicy-scout-to-probe.yaml
kubectl apply -f networkpolicy-probe-ingress.yaml
kubectl -n starfleet exec scout -- python /app/check.py
```

The line must show `ok` for `dns`, `probe` and `api`. If a step still fails, repeat the method. Then repeat the test matrix from the previous step, because a repair that opens the wanted paths must not open others: the two rows for `drifter` must still show `blocked`.

## Find pods that no policy protects

An audit also looks for pods that no policy selects. Those pods accept all traffic. List the pods and the policies per namespace and compare:

```sh
kubectl get pods --all-namespaces
kubectl get networkpolicy --all-namespaces
```

The `outpost` namespace has a pod but no policy, so the `drifter` pod is open in both directions. The `starfleet` namespace has a baseline, so every pod in it is isolated, apart from the host-networked `beacon` pod that policy does not cover. Check the same for each namespace of a cluster.

You can now use one method for any policy problem and repair a broken set. The method is: list, read, compare labels, check types and direction, confirm the plugin, test.

## Common pitfalls

> [!WARNING]
> - **Reading the policy name.** A name such as `probe-ingress` can hide an egress rule. Read the types and sections.
> - **Fixing two faults and testing once.** Faults hide each other. Test after each change.
> - **Assuming enforcement.** A cluster whose plugin ignores policy accepts them silently.
> - **Auditing only namespaces with policies.** A namespace with no policy is the biggest gap.
