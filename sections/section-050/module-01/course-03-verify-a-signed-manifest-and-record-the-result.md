---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify A Signed Manifest And Record The Result

The signature on `checksums.txt` ties the manifest to a key. If you hold the right public key from a channel you trust, a valid signature shows that the key holder produced exactly this manifest, and the digests in it can be trusted. This part verifies the signature, shows that it rejects the forged manifest from the previous part, checks the binary against the authenticated manifest, and records the result in the cluster.

## How the signature works

The publisher computes a digest of the manifest and signs it with a private key. The result is the signature, stored in `checksums.sig`. Anyone with the matching public key, `publisher.pub`, can check the signature against the digest of the manifest they hold. If the check succeeds, the manifest is unchanged since signing and was signed by the holder of the private key. The private key never leaves the publisher. In the fixture the private key was deleted after signing.

The public key itself must come from a trusted source. If an attacker can swap the public key, the attacker can sign anything. In practice you obtain the key from a separate, authenticated channel, such as the documentation of the project or a pinned copy in your own repository.

## Verify the signature

<!-- astrona:playground:renew -->

`openssl dgst -verify` takes the public key, the signature file and the signed data. To compare, first recreate the forged manifest from the previous part, because it is a file in the node container and may no longer exist:

```sh
NODE=astro-ats-031-playground-050-01-control-plane
podman exec $NODE sh -c 'sha256sum /var/lib/training-release/kubectl-tampered > /tmp/forged-checksums.txt'
podman exec $NODE openssl dgst -sha256 -verify /var/lib/training-release/publisher.pub -signature /var/lib/training-release/checksums.sig /var/lib/training-release/checksums.txt
podman exec $NODE openssl dgst -sha256 -verify /var/lib/training-release/publisher.pub -signature /var/lib/training-release/checksums.sig /tmp/forged-checksums.txt
```

The first command prints `Verified OK`. The second prints `Verification failure` and exits with a nonzero status, because the forged manifest is not what was signed. The same signature file, the same key and a different manifest give a different answer. That is the difference between integrity and authenticity.

## The order of the checks

Check in this order. First verify the signature of the manifest. Only then compare the binary with a digest from that manifest. A manifest whose signature failed is an untrusted manifest, and comparing against it proves nothing. Then check the binary:

```sh
podman exec $NODE sha256sum -c /var/lib/training-release/checksums.txt
podman exec $NODE sha256sum /var/lib/training-release/kubectl-tampered
```

The first command reports `OK`. The second prints a digest that is not the one in the authenticated manifest, so the tampered copy is rejected, and you must not run it. Remove the forged manifest:

```sh
podman exec $NODE rm /tmp/forged-checksums.txt
```

## Record the result

Evidence that was never written down cannot be reviewed later. Store the outcome as a ConfigMap in the cluster, including the digest that was verified. The commands compute the digest of the verified file and create the object:

```sh
SHA=$(podman exec $NODE sha256sum /var/lib/training-release/kubectl | cut -d' ' -f1)
kubectl -n starfleet create configmap artifact-review --from-literal=result=verified --from-literal=tampered=rejected --from-literal=sha256="$SHA"
kubectl -n starfleet get configmap artifact-review -o jsonpath='{.data}'
```

The object lists the result, the rejection of the tampered copy and the exact digest. A ConfigMap is a note and not a security control. It records what a person verified, so anyone who can edit ConfigMaps in that namespace can change the note.

## What this verification establishes

The fixture key is a local exercise key. The result shows that the manifest was signed by the holder of that key and that the staged `kubectl` matches. It does not show that the file came from the real Kubernetes project, because the key is not theirs. For the real project you need their published key or identity, which the next part covers.

## Common pitfalls

> [!WARNING]
> - **Running `sha256sum -c` before the signature check.** The manifest is not yet trusted.
> - **Trusting any valid signature.** It must come from the key you expect.
> - **Fetching the public key with the file.** A swapped key makes the check meaningless.
> - **Running the tampered copy to see what happens.** Reject it and do not execute it.
