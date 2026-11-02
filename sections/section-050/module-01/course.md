---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify Platform Binaries Before Deploying

Every Kubernetes node runs binaries that you downloaded from somewhere: `kubelet`, `kubeadm`, `kubectl`, the container runtime. Each of them runs with high privilege. If one is replaced on its way to the node, by a compromised mirror, an intercepted download or a poisoned build pipeline, the attacker gets that privilege. Verification is the step that makes sure the bytes you are about to run are the bytes the publisher released.

This module teaches you the difference between a check that detects change and a check that proves who published the file, and gives you the commands for both: `sha256sum` for digests, `openssl` for a signature made with a key, and `cosign` for signatures made with an identity. You practise the first two in the playground against a staged fixture. The third is explained as reference, because the playground has no network path to the real Kubernetes release channel.

## Learning objectives

After this module you can:

- Explain what a checksum proves, what it does not prove, and why the source of the expected digest decides its value.
- Choose the exact artifact by version, operating system and architecture, and record its digest.
- Verify a signature over a checksum manifest with a public key, and check the binary against the authenticated manifest.
- Show that a forged checksum file matches a tampered binary, and that signature verification rejects the forgery.
- Keep the verified bytes bound to what is deployed, and explain what verification does not cover.

## Before you start

You need Linux command line basics and `kubectl`. The module has four parts. The first covers the questions that verification answers and how to pick the artifact. The second shows digests at work and the limits of a bare checksum. The third verifies a signed manifest and records the result. The fourth covers keeping the binding through delivery, and signatures made with an identity.

Your playground is a `kind` cluster running Kubernetes v1.35. The control plane node container holds a staged release in `/var/lib/training-release`:

| File | What it is |
| --- | --- |
| `kubectl` | The binary to deploy |
| `kubectl-tampered` | A copy of the binary with extra bytes appended |
| `checksums.txt` | A manifest with the SHA-256 digest of `kubectl` |
| `checksums.sig` | A signature over `checksums.txt` |
| `publisher.pub` | The public key that checks the signature |

The key is a fixture made for this exercise. It stands in for a publisher key and is not the key of the real Kubernetes project.

`kubectl` already points at the playground cluster. Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
