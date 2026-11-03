---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify Packages, Images And Signatures

A checksum shows that a file did not change. A signature shows which key, or which identity, vouched for it. Cluster software arrives as operating system packages, as standalone binaries and as container images, and each channel has its own signing tools. This module covers the tools you meet on the way: GPG (the GNU Privacy Guard) for package repositories, cosign for files and images, and image digests for pinning what runs.

## Learning objectives

After this module you can:

- Verify a detached GPG signature over a file and over a repository Release file, and read the result.
- Verify a file signature with cosign and a local public key, and explain how keyless verification uses a certificate identity and an issuer.
- Find the digest of an image, pin a Deployment to it and compare it with the image identifier that a running pod reports.
- Explain what a software bill of materials lists and what verification at admission does and does not prove.

## Before you start

You need Linux command line basics, `kubectl` and `podman`. The module has six parts. The first covers GPG signed repositories. The second covers package verification on a node and is reading only. The third covers cosign with a local key pair. The fourth covers keyless verification and release signatures and is reading only. The fifth covers image digests and pinning. The sixth covers software bills of materials and verification at admission and is reading only.

Your playground is a `kind` cluster with one control plane node and one worker node. The control plane node container holds fixtures in `/var/lib/training-release/signed`. The bootstrap creates every key when the playground starts, deletes the private keys after signing, and has no network path to the real Kubernetes package repository.

| File | What it is |
| --- | --- |
| `publisher.asc`, `publisher.gpg` | The public GPG key, in text form and in keyring form |
| `release-notes.txt`, `release-notes.txt.asc` | A file and its detached GPG signature |
| `release-notes-forged.txt` | A copy of the file with a line added after signing |
| `Release`, `Release.gpg`, `Packages` | A repository-style file list and its detached signature |
| `cosign.pub` | The public key of a cosign key pair |
| `build-record.txt`, `build-record.txt.sig` | A file and its cosign signature |
| `build-record-forged.txt` | A copy of the file with a line added after signing |

The tools `gpg` and `cosign` run on the control plane node. If the node image lacks them, the bootstrap tries to install `gpg` from the package repositories and to fetch `cosign` from its project release page, which needs a network path from the node. If that fails, the bootstrap writes a marker file named `NO-GPG` or `NO-COSIGN` in the fixture directory, and the matching exercises become reading only. A fetched `cosign` binary is recorded with its digest in `cosign.fetched.sha256`, and that file only records what was downloaded; it does not prove the download genuine. All keys are fixtures and are not keys of any real project.

Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
