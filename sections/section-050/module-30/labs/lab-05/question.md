---
exam_objectives:
- Verify platform binaries before deploying
---
# Require Digest-Pinned Images At Admission

Allow about 12 minutes for the tasks.

The `starfleet` team pins every image by digest, but nothing stops a new Pod with a tag-only image. Make the API server refuse such Pods in the team's namespace, without affecting the `outpost` namespace.

## Connect to the lab

Use a shell on your own machine. The kubeconfig file holds the address and the credentials of this lab's cluster, and `kubectl` uses it.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-03-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-03-05" || exit 1
```

## Tasks

The cluster has the namespaces `starfleet-031-050-03-05` and `outpost-031-050-03-05` and no admission policy for images.

1. Create a ValidatingAdmissionPolicy that refuses a Pod when the `image` of any container or any init container does not contain `@sha256:`. A reference with both a tag and a digest, such as `docker.io/library/python:3.13-alpine@sha256:<digest>`, must be allowed.
2. Bind the policy with `validationActions: ["Deny"]` so that it applies only to Pods in `starfleet-031-050-03-05`.
3. Check with a server-side dry run that a Pod with the image `docker.io/library/python:3.13-alpine` is denied in `starfleet-031-050-03-05` and still admitted in `outpost-031-050-03-05`.

You can choose the names of the policy and the binding.
