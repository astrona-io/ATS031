# Verify And Create Blob Signatures With cosign

The fleet build system signs a build record for every component it builds. The directory `/var/lib/build-records` on the control plane node `astro-ats-031-lab-050-03-03-control-plane` holds six build records `build-<component>.txt`, a signature `<record>.sig` for most of them, and `fleet.pub`, the public key of the build system. The node has `cosign` 2.4.1 and no network access to a transparency log. Check which records really come from the build system, then sign the release approval with a new key of your own.

1. Create the ConfigMap `cosign-review` in namespace `starfleet-031-050-03-03` with the key `rejected`: the names of every build record that does not verify with `fleet.pub`, separated by spaces, for example `build-agent.txt build-relay.txt`.
2. In `/var/lib/approval`, generate a new cosign key pair with an empty password and sign `approval.txt` with it, without uploading to the transparency log, so that `/var/lib/approval/approval.txt.sig` verifies with `/var/lib/approval/cosign.pub`.
3. Delete the private key `cosign.key` from `/var/lib/approval` and keep `cosign.pub`, so that others can verify the approval.

Do not change the build records, their signatures, `fleet.pub` or `approval.txt`; the rejected records are chosen at random each time the lab starts.
