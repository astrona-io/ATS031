# Require Digest-Pinned Images At Admission — Solution

You solve this lab with one ValidatingAdmissionPolicy and one binding. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Try a Pod with a tag-only image in both namespaces. `--dry-run=server` sends the Pod through admission on the API server but stores nothing:

```sh
kubectl -n starfleet-031-050-03-05 run digest-check --image=docker.io/library/python:3.13-alpine --dry-run=server
kubectl -n outpost-031-050-03-05 run digest-check --image=docker.io/library/python:3.13-alpine --dry-run=server
```

Both print `pod/digest-check created (server dry run)`. Nothing refuses a tag-only image yet.

## Step 2: write the policy (checks `denies-tags` and `allows-digests`)

A ValidatingAdmissionPolicy holds CEL expressions that the API server evaluates for every matching request. A request passes only when every expression is `true`. The first expression requires `@sha256:` in every container image. The second does the same for init containers; `!has(...)` lets a Pod without init containers pass. `contains('@sha256:')` allows a reference with a tag and a digest as well as one with only a digest. Save this as `validatingadmissionpolicy-require-image-digest.yaml`:

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
metadata:
  name: require-image-digest
spec:
  failurePolicy: Fail
  matchConstraints:
    resourceRules:
    - apiGroups: [""]
      apiVersions: ["v1"]
      operations: ["CREATE", "UPDATE"]
      resources: ["pods"]
  validations:
  - expression: "object.spec.containers.all(c, c.image.contains('@sha256:'))"
    message: "every container image must be pinned with @sha256:<digest>"
  - expression: "!has(object.spec.initContainers) || object.spec.initContainers.all(c, c.image.contains('@sha256:'))"
    message: "every init container image must be pinned with @sha256:<digest>"
```

Apply it:

```sh
kubectl apply -f validatingadmissionpolicy-require-image-digest.yaml
```

A policy alone does nothing. It takes effect only through a binding.

## Step 3: bind the policy to one namespace (checks `denies-tags` and `outpost-unaffected`)

The binding names the policy, the action and the requests it applies to. `validationActions: ["Deny"]` rejects a failing request; `Warn` or `Audit` would only report it. Every namespace has the label `kubernetes.io/metadata.name` with its own name, so the selector matches `starfleet-031-050-03-05` and nothing else. Save this as `validatingadmissionpolicybinding-require-image-digest.yaml`:

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicyBinding
metadata:
  name: require-image-digest-starfleet
spec:
  policyName: require-image-digest
  validationActions: ["Deny"]
  matchResources:
    namespaceSelector:
      matchLabels:
        kubernetes.io/metadata.name: starfleet-031-050-03-05
```

Apply it:

```sh
kubectl apply -f validatingadmissionpolicybinding-require-image-digest.yaml
```

## Step 4: test the policy

Run the same dry runs as in Step 1, plus one with a digest. The API server can take a few seconds to load a new policy, so repeat a command if its result has not changed yet:

```sh
kubectl -n starfleet-031-050-03-05 run digest-check --image=docker.io/library/python:3.13-alpine --dry-run=server
kubectl -n starfleet-031-050-03-05 run digest-check --image=docker.io/library/python:3.13-alpine@sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef --dry-run=server
kubectl -n outpost-031-050-03-05 run digest-check --image=docker.io/library/python:3.13-alpine --dry-run=server
```

The first command fails with `ValidatingAdmissionPolicy 'require-image-digest' with binding 'require-image-digest-starfleet' denied request`. The second and the third print `pod/digest-check created (server dry run)`. The digest in the second command does not have to exist, because a dry run never pulls the image.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not check only `object.spec.containers`. The grader also sends a Pod whose init container has a tag-only image, and it must be denied too.
>
> Do not test for a missing `:` in the image. A reference with both a tag and a digest must be admitted.
>
> Do not bind with `Warn` or `Audit` only. The grader requires `validationActions: ["Deny"]`.
>
> Do not leave out `matchResources` or select every namespace. A tag-only Pod in `outpost-031-050-03-05` must still be admitted.
