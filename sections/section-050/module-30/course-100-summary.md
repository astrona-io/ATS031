# Summary

A checksum shows that a file did not change. A signature shows which key or identity vouched for it. A signed repository uses both in a chain: one signature on the `Release` file covers the package index, and the index covers each package through digests.

`gpg --verify` with a named keyring reports a good signature for the original bytes, and a bad signature for a file that changed afterwards. The warning that a key is not certified is not a failure. The public key itself remains the trust decision, so compare its fingerprint through a second channel.

Package managers can compare installed files with the digests they recorded at install time, with commands such as `dpkg --verify` and `rpm -V`. These records sit on the same machine as the files, and they do not cover files that no package installed. So the results find accidents, not a careful attacker.

cosign verifies a file with a public key in the same way, and it can also sign images in a registry. Without network access, it skips the transparency log, and that choice removes the evidence of when something was signed.

Keyless signing replaces the long lived private key with a short lived certificate that names an identity and an issuer. The verifier must state both, and must read them from the official documentation of the release. A valid signature from any identity proves nothing.

A tag can move, while a digest names content. Pin an image by writing the digest into the `image` field. Then read the `imageID` of the running pod and check that it carries the same digest. The form of the identifier depends on how the image reached the node, so read it before you compare.

A software bill of materials lists the components of an artifact, and it is only as trustworthy as its signature. Admission control can refuse unsigned or unpinned images when they are created. For that, the policy must require digests, state the expected key or identity, fail closed and keep its exemptions small. None of these controls shows that software is free of vulnerabilities.

Key facts to remember:

- A signature covers exact bytes; a changed file fails.
- The key or the identity is the trust decision.
- A keyless check needs the expected identity and issuer.
- Pin by digest and compare with the running `imageID`.
- Admission checks happen when an object is created or updated.

<!-- astrona:playground:destroy -->
