---
exam_objectives:
- Verify platform binaries before deploying
---
# Require Digest-Pinned Images At Admission: Solution

Connect to the lab first, so that `kubectl` talks to this lab's cluster:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-03-05)"
```

A ValidatingAdmissionPolicy holds the rule, written in the Common Expression Language (CEL). A ValidatingAdmissionPolicyBinding says where the rule applies and what the API server does when it fails. The API server evaluates both itself, so no webhook or extra component is needed.

## Write the policy

The policy matches Pods on `CREATE` and `UPDATE`. One expression checks every container and a second checks every init container. A Pod without init containers has no `initContainers` field, so the second expression first tests for it with `has()`. `failurePolicy: Fail` makes the API server refuse the request if the expression cannot be evaluated. Save this as `validatingadmissionpolicy-require-image-digest.yaml`:

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

```text
validatingadmissionpolicy.admissionregistration.k8s.io/require-image-digest created
```

The policy alone does nothing. The API server enforces it only through a binding.

## Bind it to one namespace

Every namespace carries the label `kubernetes.io/metadata.name` with its own name, so a `namespaceSelector` on that label selects exactly one namespace. `validationActions: ["Deny"]` makes a failed check reject the request. Save this as `validatingadmissionpolicybinding-require-image-digest.yaml`:

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

```text
validatingadmissionpolicybinding.admissionregistration.k8s.io/require-image-digest-starfleet created
```

## Check the result

`--dry-run=server` sends the request through admission without storing the object. Wait a few seconds after the binding, then send a tag-only Pod to the bound namespace:

```sh
kubectl -n starfleet-031-050-03-05 run relay --image=docker.io/library/python:3.13-alpine --dry-run=server
```

```text
The pods "relay" is invalid: : ValidatingAdmissionPolicy 'require-image-digest' with binding 'require-image-digest-starfleet' denied request: every container image must be pinned with @sha256:<digest>
```

The message names the policy, the binding and the failed expression's message. A reference with a tag and a digest passes, and the same tag-only Pod still passes in the other namespace:

```sh
kubectl -n starfleet-031-050-03-05 run relay --image=docker.io/library/python:3.13-alpine@sha256:673651b211bd81589d3a8688d65200b44565d6ecb0cd5bb0205b31a067f4b5e6 --dry-run=server
kubectl -n outpost-031-050-03-05 run relay --image=docker.io/library/python:3.13-alpine --dry-run=server
```

```text
pod/relay created (server dry run)
pod/relay created (server dry run)
```

The grader sends its own dry-run Pods: a tag-only container and a tag-only init container in `starfleet-031-050-03-05` must be denied by a ValidatingAdmissionPolicy, Pods with digest references must be admitted there, and a tag-only Pod must be admitted in `outpost-031-050-03-05`.
