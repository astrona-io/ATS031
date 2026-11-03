---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify platform binaries before deploying

A binary arrives on a node and runs with high privilege. A checksum from the same place as the file proves only that the download was intact. This section teaches the difference between integrity and authenticity, how to verify a signed manifest and the binary against it, and how to keep the verified bytes bound to what is deployed.

## Learning Path

1. Verify Platform Binaries Before Deploying: the first module, with the playground and a signed-manifest lab. It covers integrity, authenticity, digests, a signed manifest and keeping the verified bytes bound to what is deployed.
2. Verify Kubernetes Release Binaries Hands-On: the release layout, the `sha256sum --check` format, tampered and wrong-architecture files, binary versions, and the `kubelet` that runs on a node. Two labs.
3. Verify Packages, Images And Signatures: GPG signed repositories, package verification, cosign with a local key pair, keyless verification as reading, image digests and pinning, SBOMs and admission-time verification. Two labs.
4. Capstone: verify a signed release bundle, check the running `kubelet`, pin an image by digest and record a verification report.

Each module ends with a summary and a ten-question knowledge check. The deep-dive parts carry the hands-on steps, and each lab follows the part that practises its skill. Every playground is a private `kind` cluster with Kubernetes v1.35 and no outside network path; launch it from the landing page and keep it running while you read.

## Learning Outcomes

- Explain what a checksum proves, what it does not prove, and why the source of the expected digest decides its value.
- Choose the exact artifact by version, operating system and architecture, and record its digest.
- Verify a signature over a checksum manifest with a public key, and check the binary against the authenticated manifest.
- Show that a forged checksum file matches a tampered binary, and that signature verification rejects the forgery.
- Keep the verified bytes bound to what is deployed, and explain what verification does not cover.
- Build the checksum check for a Kubernetes release file in the exact `digest  file name` form, and read its exit status.
- Detect a tampered file, a file for the wrong architecture and a stale checksum file.
- Read the version of `kubectl`, `kubeadm` and `kubelet`, and verify the binary that a node runs through `/proc/<pid>/exe`.
- Verify GPG and cosign signatures with a local key, and explain what keyless verification and package verification add.
- Pin an image by digest and compare it with the `imageID` of the running pod.
