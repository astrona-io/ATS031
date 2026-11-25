---
exam_objectives:
- Verify platform binaries before deploying
---
# Verify A Signed Checksum Manifest: Solution

Connect to the lab first, so that `kubectl` talks to this lab's cluster and `$node_name` names its control plane node:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-01-02)"
node_name="astro-ats-031-lab-050-01-02-control-plane"
RELEASE=/var/lib/relay-release
```

## Verify the signature of each manifest

`openssl dgst -sha256 -verify` takes the public key, the signature file and the signed file. It prints `Verified OK` and exits with 0 when the signature was made with the matching private key over exactly these bytes. Otherwise it prints `Verification failure` and exits with 1. Run it once for each mirror:

```sh
podman exec "$node_name" openssl dgst -sha256 -verify $RELEASE/publisher.pub -signature $RELEASE/mirror-a/SHA256SUMS.sig $RELEASE/mirror-a/SHA256SUMS
podman exec "$node_name" openssl dgst -sha256 -verify $RELEASE/publisher.pub -signature $RELEASE/mirror-b/SHA256SUMS.sig $RELEASE/mirror-b/SHA256SUMS
podman exec "$node_name" openssl dgst -sha256 -verify $RELEASE/publisher.pub -signature $RELEASE/mirror-c/SHA256SUMS.sig $RELEASE/mirror-c/SHA256SUMS
```

Two mirrors print `Verified OK`. One prints `Verification failure`: its manifest was signed with another key. Its binary and manifest still agree with each other, which is exactly why a checksum alone is not enough.

## Check the binary against the authenticated manifests

Only a manifest with a good signature is worth a comparison. Check the binary of the two mirrors that passed:

```sh
podman exec -w $RELEASE/mirror-a "$node_name" sha256sum --check SHA256SUMS
podman exec -w $RELEASE/mirror-b "$node_name" sha256sum --check SHA256SUMS
podman exec -w $RELEASE/mirror-c "$node_name" sha256sum --check SHA256SUMS
```

On one of the signed mirrors `relay-agent` reports `FAILED`: the publisher signed the manifest, but the binary changed after that. The mirror that has `Verified OK` and `relay-agent: OK` is the genuine release.

## Record the result

Read the digest from the authenticated manifest of that mirror. The example uses `b`; use your own letter:

```sh
TRUSTED_DIGEST=$(podman exec "$node_name" cut -d' ' -f1 $RELEASE/mirror-b/SHA256SUMS)
kubectl -n starfleet-031-050-01-02 create configmap artifact-review \
  --from-literal=mirror=b --from-literal=sha256="$TRUSTED_DIGEST"
kubectl -n starfleet-031-050-01-02 get configmap artifact-review -o yaml
```

The grader repeats both checks on each mirror, finds the one that passes both, and compares it with your record. The order matters in practice too: verify the signature first, then trust the digests in the manifest.
