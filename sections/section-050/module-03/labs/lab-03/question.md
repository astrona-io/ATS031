---
exam_objectives:
- Verify platform binaries before deploying
---
# Verify And Create Blob Signatures With cosign

Allow about 12 minutes for the tasks.

The fleet build system signs a build record for every component it builds. Before the `starfleet` cluster takes a new release, check which records really come from the build system, then sign the release approval with a new key of your own.

## Connect to the lab

Use a shell on your own machine. The kubeconfig file holds the address and the credentials of this lab's cluster, and `kubectl` uses it.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-03-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-03-03" || exit 1
node_name="astro-ats-031-lab-050-03-03-control-plane"
```

The node of a `kind` cluster is a container on your machine. Run a command inside it with `podman exec "$node_name" <command>`. If your machine uses Docker, write `docker exec` instead. The node has `cosign` 2.4.1 in `/usr/local/bin` and no network access to a transparency log.

## Tasks

The directory `/var/lib/build-records` on the control plane node holds six build records `build-<component>.txt`, a signature `<record>.sig` for most of them, and `fleet.pub`, the public key of the build system.

1. Verify every build record with `cosign verify-blob` and the key `fleet.pub`. Skip the transparency log check, because the node cannot reach it.
2. Create the ConfigMap `cosign-review` in the namespace `starfleet-031-050-03-03` with the key `rejected`: the names of every build record that does not verify, separated by spaces, for example `build-agent.txt build-relay.txt`.
3. In `/var/lib/approval` on the control plane node, generate a new cosign key pair with an empty password. Sign `approval.txt` with the private key, without uploading to the transparency log, and write the signature to `/var/lib/approval/approval.txt.sig`.
4. Delete the private key `cosign.key` from `/var/lib/approval`. Keep `cosign.pub`, so that others can verify the approval.

Do not change the build records, their signatures or `fleet.pub`. The rejected records are chosen at random each time the lab starts.
