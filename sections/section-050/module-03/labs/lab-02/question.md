---
exam_objectives:
- Verify platform binaries before deploying
---
# Verify A Signed apt Repository And An Installed Package

Allow about 12 minutes for the tasks.

The control plane node of the `starfleet` cluster has a local copy of the fleet apt repository, and the `fleet-tools` package from it is installed. Follow the chain of trust from the signed `Release` file down to each package file, then check the installed files of `fleet-tools`.

## Connect to the lab

Use a shell on your own machine. The kubeconfig file holds the address and the credentials of this lab's cluster, and `kubectl` uses it.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-03-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-03-02" || exit 1
node_name="astro-ats-031-lab-050-03-02-control-plane"
```

The node of a `kind` cluster is a container on your machine. Run a command inside it with `podman exec "$node_name" <command>`. If your machine uses Docker, write `docker exec` instead.

## Tasks

The repository is in `/var/lib/fleet-apt` on the control plane node. It holds `Release`, its detached signature `Release.gpg`, the package index `Packages`, the package files in `pool/`, and `fleet-archive.gpg`, a keyring with the public key of the archive.

1. Verify `Release.gpg` with `gpgv` and the keyring `fleet-archive.gpg`.
2. Check the digest of `Packages` against the `SHA256:` list in `Release`.
3. Check the digest of every package file in `pool/` against its `SHA256:` field in `Packages`.
4. Ask `dpkg` which installed file of `fleet-tools` no longer matches the package.
5. Create the ConfigMap `repository-review` in the namespace `starfleet-031-050-03-02` with two keys:
   - `bad-package`: the file name of the package whose digest differs from `Packages`, for example `fleet-agent_2.0.1_all.deb`.
   - `changed-file`: the full path of the installed `fleet-tools` file that `dpkg` reports as changed.

Do not change the repository, and do not reinstall or remove any package. The damaged package and the changed file are chosen at random each time the lab starts.
