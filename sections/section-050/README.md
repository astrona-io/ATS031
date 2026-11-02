---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify platform binaries before deploying

A binary arrives on a node and runs with high privilege. A checksum from the same place as the file proves only that the download was intact. This section teaches the difference between integrity and authenticity, how to verify a signed manifest and the binary against it, and how to keep the verified bytes bound to what is deployed.

## Learning Path

1. Verify Platform Binaries Before Deploying: the landing page and the playground.
2. Integrity, Authenticity And The Exact Artifact
3. Digests At Work And The Limits Of A Checksum
4. Verify A Signed Manifest And Record The Result
5. Keep The Binding Through Delivery, And Identity-Based Signatures
6. Summary, then the ten-question knowledge check.

The parts carry the hands-on steps. Each lab follows the part that practises its skill. The playground is a private `kind` cluster with Kubernetes v1.35; launch it from the landing page and keep it running while you read.

## Learning Outcomes

- Explain what a checksum proves, what it does not prove, and why the source of the expected digest decides its value.
- Choose the exact artifact by version, operating system and architecture, and record its digest.
- Verify a signature over a checksum manifest with a public key, and check the binary against the authenticated manifest.
- Show that a forged checksum file matches a tampered binary, and that signature verification rejects the forgery.
- Keep the verified bytes bound to what is deployed, and explain what verification does not cover.
