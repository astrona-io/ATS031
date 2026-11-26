# Require Digest-Pinned Images At Admission

The `starfleet` team pins every image by digest, but nothing stops a new Pod with a tag-only image. The cluster has the namespaces `starfleet-031-050-03-05` and `outpost-031-050-03-05` and no admission policy for images. Make the API server refuse such Pods in the team's namespace, without affecting the `outpost` namespace.

1. Create a ValidatingAdmissionPolicy, bound to Pods in `starfleet-031-050-03-05`, that denies a Pod when the `image` of any container or any init container does not contain `@sha256:`, so that a Pod with the image `docker.io/library/python:3.13-alpine` is denied there.
2. A Pod in `starfleet-031-050-03-05` whose image has a digest, with or without a tag, such as `docker.io/library/python:3.13-alpine@sha256:<digest>`, must still be admitted.
3. Bind the policy with `validationActions: ["Deny"]` and only to `starfleet-031-050-03-05`, so that a Pod with a tag-only image is still admitted in `outpost-031-050-03-05`.

You can choose the names of the policy and the binding; do not change the namespaces.
