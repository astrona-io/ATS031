---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# cosign With A Local Key Pair

GPG signs repository files. For single files and container images, many projects use cosign, a command line tool of the Sigstore project that signs and verifies blobs (any file) and images. This part verifies a signed file with a local public key, shows a forged file failing, and creates a new key pair of your own to see the full signing round trip.

## Key-based verification

A key pair has a private key that signs and a public key that verifies. `cosign verify-blob` takes the public key, the signature file and the blob. It recomputes the digest of the blob and checks the signature against it. A blob that changed after signing fails, as with GPG. The difference is in the ecosystem: cosign signatures can be stored next to images in a registry, and cosign can also record signing events in a public transparency log named Rekor.

A transparency log is an append-only public list of signing events, and a log entry gives evidence of when something was signed. A key-based exercise without network access cannot reach Rekor, so the commands below switch it off. Flag names have changed between cosign versions. The commands follow the behavior of cosign 2.x. Run the `--help` output of `cosign sign-blob` and `cosign verify-blob` on your version when a flag is rejected.

## Verify the fixture

The fixture directory holds `cosign.pub`, `build-record.txt` and its signature. If the listing there contains `NO-COSIGN`, the node has no `cosign`, and this part is reading only.

<!-- astrona:playground:renew -->

```sh
NODE=astro-ats-031-playground-050-03-control-plane
SIGNED=/var/lib/training-release/signed
podman exec $NODE ls $SIGNED
podman exec $NODE cosign version
podman exec -w $SIGNED $NODE cosign verify-blob --key cosign.pub --signature build-record.txt.sig --insecure-ignore-tlog=true build-record.txt
```

The first command lists the fixtures, the second prints the tool version and the third verifies the blob and prints `Verified OK`. The option `--insecure-ignore-tlog=true` tells cosign to skip the transparency log check. The name contains the word insecure on purpose: without the log, nothing shows when the signature was made. Now verify the forged copy against the same signature:

```sh
podman exec -w $SIGNED $NODE cosign verify-blob --key cosign.pub --signature build-record.txt.sig --insecure-ignore-tlog=true build-record-forged.txt
echo "exit status: $?"
```

Verification fails with an error about the signature and the exit status is nonzero. One added line changed the digest, and the signature no longer fits.

## Create a key pair and sign a file

To see the round trip, make your own pair in a scratch directory on the node. `cosign generate-key-pair` writes `cosign.key` and `cosign.pub`. It asks for a password for the private key. Setting `COSIGN_PASSWORD` to an empty value skips the question, which is acceptable for a throwaway key and not for a real one.

```sh
podman exec -w /tmp $NODE sh -c "COSIGN_PASSWORD='' cosign generate-key-pair"
podman exec -w /tmp $NODE sh -c "echo 'my record' > my-record.txt && COSIGN_PASSWORD='' cosign sign-blob --yes --key cosign.key --tlog-upload=false --output-signature my-record.sig my-record.txt"
podman exec -w /tmp $NODE cosign verify-blob --key cosign.pub --signature my-record.sig --insecure-ignore-tlog=true my-record.txt
```

The last command prints `Verified OK`. The private key never leaves the signer in a real process. Remove the scratch files, including the private key, when you finish:

```sh
podman exec -w /tmp $NODE rm -f cosign.key cosign.pub my-record.txt my-record.sig
```

## Images and the limits of a local key

Cosign also signs container images with `cosign sign --key` and checks them with `cosign verify --key`. Both commands talk to a container registry, because the signature is stored there next to the image. The playground has no registry, so image signatures are reading only. The command identifies the image by digest, and you should always verify and deploy the digest, because a tag can move after the check.

A local key pair moves the trust question to the key. Whoever holds the public key you verify with decides who you trust. The file `cosign.fetched.sha256`, if the bootstrap created it, records the digest of the `cosign` binary it downloaded without a signature check, which is a small example of the same problem.

You can now verify a signed file with a public key and make your own signature. The question is how to avoid a long lived private key altogether.

## Common pitfalls

> [!WARNING]
> - **Leaving `--insecure-ignore-tlog` in a real pipeline.** It removes the evidence of when and by whom something was signed.
> - **Using an empty key password outside an exercise.** The private key is then unprotected.
> - **Taking the public key from the place that hosts the file.** Obtain it from a separate trusted channel.
> - **Verifying an image by tag.** The tag can point to another image tomorrow; verify the digest.
