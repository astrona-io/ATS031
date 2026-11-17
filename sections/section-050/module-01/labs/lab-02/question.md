---
exam_objectives:
- Verify platform binaries before deploying
---
# Verify A Signed Checksum Manifest

Allow about 10 minutes for the tasks.

The `relay-agent` binary is offered on three mirrors. Each mirror ships the binary, a `SHA256SUMS` manifest and a signature over the manifest. Only one mirror has the release that the publisher signed. Find it before the binary goes to the `starfleet` nodes.

## Connect to the lab

Use a shell on your own machine. The kubeconfig file holds the address and the credentials of this lab's cluster, and `kubectl` uses it.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-01-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-01-02" || exit 1
node_name="astro-ats-031-lab-050-01-02-control-plane"
```

The node of a `kind` cluster is a container on your machine. Run a command inside it with `podman exec "$node_name" <command>`. If your machine uses Docker, write `docker exec` instead.

## Tasks

The directory `/var/lib/relay-release` on the control plane node holds the publisher's public key `publisher.pub` and the folders `mirror-a`, `mirror-b` and `mirror-c`. Each folder has `relay-agent`, `SHA256SUMS` and `SHA256SUMS.sig`. The signature is an RSA signature over the SHA-256 digest of `SHA256SUMS`, made with `openssl dgst -sha256 -sign`.

1. For each mirror, verify `SHA256SUMS.sig` over `SHA256SUMS` with `publisher.pub`.
2. For each mirror, check `relay-agent` against its `SHA256SUMS`.
3. Find the one mirror that passes both checks.
4. Create the ConfigMap `artifact-review` in the namespace `starfleet-031-050-01-02` with two keys:
   - `mirror`: the letter of that mirror, `a`, `b` or `c`.
   - `sha256`: the `relay-agent` digest listed in that mirror's authenticated `SHA256SUMS`.

Do not run `relay-agent`, and do not change the staged files. The roles of the mirrors are chosen at random each time the lab starts.
