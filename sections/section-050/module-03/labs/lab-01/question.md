---
exam_objectives:
- Verify platform binaries before deploying
---
# Verify Detached GPG Signatures With gpgv

Allow about 10 minutes for the tasks.

The fleet publisher sends six operations documents to the control plane node of the `starfleet` cluster, each with a detached GPG signature. Some documents did not arrive as the publisher signed them. Find them before anyone acts on them.

## Connect to the lab

Use a shell on your own machine. The kubeconfig file holds the address and the credentials of this lab's cluster, and `kubectl` uses it.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-03-01" || exit 1
node_name="astro-ats-031-lab-050-03-01-control-plane"
```

The node of a `kind` cluster is a container on your machine. Run a command inside it with `podman exec "$node_name" <command>`. If your machine uses Docker, write `docker exec` instead.

## Tasks

The directory `/var/lib/doc-review` on the control plane node holds six `.txt` documents, a detached ASCII-armored signature `<document>.asc` for most of them, and `publisher.gpg`, a keyring file with only the publisher's public key. The node has `gpgv`, the GnuPG tool that only verifies signatures; it has no `gpg`.

1. Verify each document against its signature, trusting only the keys in `publisher.gpg`.
2. Create the ConfigMap `signature-review` in the namespace `starfleet-031-050-03-01` with two keys:
   - `rejected`: the names of every document that does not have a good signature from the publisher key, separated by spaces, for example `crew-roster.txt nav-update.txt`.
   - `fingerprint`: the full 40-character fingerprint of the publisher key, as `gpgv` prints it.

Do not change the documents, the signatures or the keyring. The rejected documents are chosen at random each time the lab starts.
