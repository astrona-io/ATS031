# Summary

Verification answers separate questions. Integrity asks whether the bytes match an expected digest. Authenticity asks whether the expected publisher produced those bytes. Suitability, which means vulnerabilities and compatibility, is a different review, and neither check covers it.

A checksum from the same place as the file only proves that the download was not damaged. An attacker who controls both the file and the checksum can supply a matching pair. So the value of a digest depends on where the expected digest comes from.

Choose the artifact by component, version, operating system and architecture, and record its digest. The `sha256sum` command computes a digest, and `sha256sum -c` compares a file with a manifest. A forged manifest passes that comparison for a tampered binary, so you must prove that the manifest is authentic first.

With a key-based signature, `openssl dgst -verify` and the trusted public key return `Verified OK` for the real manifest and `Verification failure` for a forged one. Verify the signature first, and only then compare the binary with the trusted manifest. A record of the result, such as a ConfigMap, is a note for later review and not a security control.

Identity-based signing with `cosign verify-blob` checks a certificate that names the signer. It needs the expected identity and the expected issuer, because a valid signature from any signer is not enough. In every case, the trust decision depends on where the key, the identity and the issuer come from.

Keep the link between the check and the deployment. Verify the copy at its final location, and store it in a directory that only the deployment user can write to. Deploy images by digest, make the pipeline fail when verification is missing, and record what you verified. The key in the playground is an exercise key and says nothing about the real Kubernetes publisher.

Key facts to remember:

- A digest detects change; a signature on the manifest shows who vouched for it.
- Verify the signature before you trust the digests in the manifest.
- Pin by digest, and verify where the file is installed.
- A writable directory lets others replace even a read-only file.
- Authenticity is not a vulnerability review.

<!-- astrona:playground:destroy -->
