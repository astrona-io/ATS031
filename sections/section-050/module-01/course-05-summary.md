---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Summary

Verification answers separate questions. Integrity asks whether the bytes match an expected digest. Authenticity asks whether the expected publisher produced them. Suitability, meaning vulnerabilities and compatibility, is a different review and is not covered by either. A checksum from the same place as the file proves only that the download was intact, because an attacker who controls both can supply a matching pair.

Choose the artifact by component, version, operating system and architecture, and record its digest. Use `sha256sum` to compute a digest and `sha256sum -c` to compare a file with a manifest. A forged manifest passes that comparison for a tampered binary, so authenticate the manifest first. With a key-based signature, `openssl dgst -verify` with the trusted public key returns `Verified OK` for the real manifest and `Verification failure` for a forged one. Verify the signature first and then compare the binary with the authenticated manifest.

Identity-based signing with `cosign verify-blob` checks a certificate that names the signer, and it needs the expected identity and issuer, because a valid signature from any signer is not enough. The trust decision depends on where the key, the identity and the issuer come from.

Keep the binding through delivery. Verify the copy at its final location, store it where only the deployment user can write, deploy images by digest, fail the pipeline when verification is missing, and record what you verified. The playground fixture key is an exercise trust root and says nothing about the real Kubernetes publisher.

Key facts to remember:

- A digest detects change; a signature on the manifest shows who vouched for it.
- Verify the signature before you trust the digests in the manifest.
- Pin by digest, and verify where the file is installed.
- Authenticity is not a vulnerability review.

<!-- astrona:playground:destroy -->
