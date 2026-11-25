# SBOMs And Admission-Time Verification

Knowing which image runs is one question. Knowing what is inside it, and stopping an unverified image from starting, are two more. This part describes the software bill of materials and the checks a cluster can make when an object is created. Signature checks at admission need a policy engine that the playground does not install, but the API server can check the image reference itself, and you will build such a check in the playground.

## What an SBOM lists

A software bill of materials (SBOM) is a machine readable list of the components inside an artifact: packages, libraries, their versions and often their licenses and sources. Two common formats are SPDX and CycloneDX. A scanner can compare the list with a database of known vulnerabilities, so when a new vulnerability is published you search your SBOMs instead of unpacking every image.

An SBOM is a statement made by whoever produced it. A list generated at build time from the build inputs can be wrong or incomplete, and a list that is not signed can be replaced. For that reason an SBOM is often attached to an image as a signed attestation, a signed statement that is bound to the image digest. Verifying the signature on the attestation, and the digest it names, is what links the list to the image.

## Verification at admission

The Kubernetes API server runs admission control before it stores an object. A validating admission webhook, or a ValidatingAdmissionPolicy, can refuse a Pod whose image does not meet a rule. Policy engines such as Kyverno or the Sigstore policy controller implement rules like "every image must have a valid signature from this key or identity, and must be referenced by digest". When the rule fails, the API server rejects the Pod at creation, before any container starts.

For the check to be meaningful, the policy must require the digest form, because a tag could resolve to another image after the check. The policy must state the expected key or the expected identity and issuer, as in the keyless model. The webhook must fail closed, so a webhook outage does not let unverified images in, and the exemptions, such as system namespaces, must be small and reviewed.

```mermaid
flowchart TB
    U["kubectl apply"] --> A["API server"]
    A -->|"admission request"| W["Policy engine"]
    W -->|"checks signature and digest"| R["Registry"]
    W -->|"allow or deny"| A
    A -->|"stores the object"| E["etcd"]
```

The diagram shows the policy engine deciding before the object is stored.

## A rule inside the API server

A ValidatingAdmissionPolicy is a Kubernetes object that holds a rule written in the Common Expression Language (CEL). The API server evaluates the rule itself, so no webhook and no extra component are involved. A ValidatingAdmissionPolicyBinding is a second object that says which requests the rule applies to and what the API server does when it fails. CEL cannot fetch a signature from a registry, so this kind of policy checks only what the request contains, such as the text of each image reference.

The example policy below allows only images from `docker.io/library/`. Its `matchConstraints` select Pod requests, and the expression must be true for every container. `failurePolicy: Fail` makes the API server refuse the request if the expression cannot be evaluated. Save this as `validatingadmissionpolicy-allowed-registry.yaml`:

<!-- astrona:playground:renew -->

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
metadata:
  name: allowed-registry
spec:
  failurePolicy: Fail
  matchConstraints:
    resourceRules:
    - apiGroups: [""]
      apiVersions: ["v1"]
      operations: ["CREATE", "UPDATE"]
      resources: ["pods"]
  validations:
  - expression: "object.spec.containers.all(c, c.image.startsWith('docker.io/library/'))"
    message: "every container image must come from docker.io/library/"
```

Apply it:

```sh
kubectl apply -f validatingadmissionpolicy-allowed-registry.yaml
```

```text
validatingadmissionpolicy.admissionregistration.k8s.io/allowed-registry created
```

The policy has no effect yet, because the API server enforces a policy only through a binding. The binding below applies the rule to the `outpost` namespace only. Every namespace carries the label `kubernetes.io/metadata.name` with its own name, so the selector matches exactly one namespace. `validationActions: ["Deny"]` makes a failed rule reject the request. Save this as `validatingadmissionpolicybinding-allowed-registry.yaml`:

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicyBinding
metadata:
  name: allowed-registry-outpost
spec:
  policyName: allowed-registry
  validationActions: ["Deny"]
  matchResources:
    namespaceSelector:
      matchLabels:
        kubernetes.io/metadata.name: outpost
```

Apply it:

```sh
kubectl apply -f validatingadmissionpolicybinding-allowed-registry.yaml
```

```text
validatingadmissionpolicybinding.admissionregistration.k8s.io/allowed-registry-outpost created
```

Now test the rule without creating anything. `--dry-run=server` sends the request through admission control and then discards it. Wait a few seconds after the binding, then ask for a test pod `drifter-check` from another registry in `outpost`. The name differs from the `drifter` pod that already runs there:

```sh
kubectl -n outpost run drifter-check --image=registry.example.com/drifter:1.0 --dry-run=server
```

```text
The pods "drifter-check" is invalid: : ValidatingAdmissionPolicy 'allowed-registry' with binding 'allowed-registry-outpost' denied request: every container image must come from docker.io/library/
```

The API server rejected the request and named the policy, the binding and the message. The same request for an allowed image, and the same request in the `starfleet` namespace, both pass:

```sh
kubectl -n outpost run drifter-check --image=docker.io/library/busybox:1.37.0 --dry-run=server
kubectl -n starfleet run drifter-check --image=registry.example.com/drifter:1.0 --dry-run=server
```

```text
pod/drifter-check created (server dry run)
pod/drifter-check created (server dry run)
```

The same pattern can require a digest in every image reference, which closes the gap that a tag leaves. A rule that also checks `initContainers` must first test that the field exists, because a Pod without init containers does not have it. Remove the example when you are done with `kubectl delete validatingadmissionpolicybinding allowed-registry-outpost` and `kubectl delete validatingadmissionpolicy allowed-registry`.

## What these checks do not prove

A signature shows who signed, not that the content is safe. Admission checks only objects that are created or updated; a Pod that started before the policy existed keeps running until it is replaced. An SBOM lists components and does not list vulnerabilities, bugs or malicious logic in them. A signed image from a trusted builder can still contain a vulnerable library. Each control answers one question, and the controls work together: pinned digest, valid signature, a current component list and an admission rule that enforces them.

You can now say what an SBOM contains and where signature checking fits in the cluster. You can also write an admission rule that the API server enforces in one namespace, and you know the limit of each control.

## Common pitfalls

> [!WARNING]
> - **Trusting an unsigned SBOM.** Anyone can write one.
> - **Writing an admission policy that accepts tags.** Require digests.
> - **Letting the webhook fail open.** A failure of the policy engine must block, not allow.
> - **Assuming old pods are covered.** Admission applies when an object is created or updated.
> - **Creating a policy without a binding.** The API server enforces nothing until a binding names the policy.
> - **Expecting a CEL rule to check signatures.** It sees only the request; signature checks need a policy engine that can reach the registry.
