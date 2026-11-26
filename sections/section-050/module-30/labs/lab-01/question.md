# Verify Detached GPG Signatures With gpgv

The fleet publisher sent six operations documents to `/var/lib/doc-review` on the control plane node `astro-ats-031-lab-050-03-01-control-plane`. The directory holds the `.txt` documents, a detached ASCII-armored signature `<document>.asc` for most of them, and `publisher.gpg`, a keyring with only the publisher's public key. The node has `gpgv` and no `gpg`. Record your findings in the ConfigMap `signature-review` in namespace `starfleet-031-050-03-01`.

1. Set the key `rejected` to the names of every document that does not have a good signature from a key in `publisher.gpg`, separated by spaces, for example `crew-roster.txt nav-update.txt`.
2. Make sure `rejected` names no document that has a good signature from the publisher key.
3. Set the key `fingerprint` to the full 40-character fingerprint of the publisher key, as `gpgv` prints it.

Do not change the documents, the signatures or the keyring; the rejected documents are chosen at random each time the lab starts.
