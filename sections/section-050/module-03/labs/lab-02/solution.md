---
exam_objectives:
- Verify platform binaries before deploying
---
# Verify A Signed apt Repository And An Installed Package: Solution

Connect to the lab first, so that `kubectl` talks to this lab's cluster and `$node_name` names its control plane node. All commands below run in a shell inside the node, in the repository directory:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-03-02)"
node_name="astro-ats-031-lab-050-03-02-control-plane"
podman exec -it -w /var/lib/fleet-apt "$node_name" bash
```

The keys, digests and random choices are new on every start. The output below comes from one run.

## Verify the signed Release file

Only `Release` carries a signature. Everything else is trusted because `Release` lists its digest. So check the signature first:

```sh
gpgv --keyring ./fleet-archive.gpg Release.gpg Release
```

```text
gpgv: Signature made Tue Nov 17 19:56:58 2026 UTC
gpgv:                using RSA key ECDF86F9E5DF4DD8F3621180F1A50B45B8FCE45B
gpgv:                issuer "archive@fleet.example"
gpgv: Good signature from "Fleet Archive <archive@fleet.example>"
```

## Check Packages against Release

The `SHA256:` list at the end of `Release` gives the digest and the size of `Packages`. Compare it with the digest of the file:

```sh
cat Release
sha256sum Packages
```

```text
SHA256:
 a116ba8799bd0fc1a7cf59ffff5c1820d9484d89b2666b7b3c5efbad9658a2a1 1254 Packages
a116ba8799bd0fc1a7cf59ffff5c1820d9484d89b2666b7b3c5efbad9658a2a1  Packages
```

The first lines of `Release` are left out above. The two digests are equal, so `Packages` is the index the archive signed.

## Check every package file against Packages

Each stanza in `Packages` has a `Filename:` and a `SHA256:` field. `awk` turns them into lines in the check format, and `sha256sum --check` reads those lines from standard input:

```sh
awk '/^Filename:/ {file=$2} /^SHA256:/ {print $2 "  " file}' Packages | sha256sum --check
```

```text
pool/fleet-agent_2.0.1_all.deb: OK
pool/fleet-docs_1.0.0_all.deb: OK
pool/fleet-probe_0.9.7_all.deb: OK
pool/fleet-tools_1.4.2_all.deb: FAILED
sha256sum: WARNING: 1 computed checksum did NOT match
```

In this run `fleet-tools_1.4.2_all.deb` changed after the archive published the index. `apt` would refuse to install it for the same reason. The copy of `fleet-tools` on the node was installed before the change, so its installed files need their own check.

## Check the installed files of fleet-tools

A good package file says nothing about the files on disk after the install. `dpkg --verify` (short form `dpkg -V`) compares each installed file with the MD5 digest that the package shipped in its `md5sums` list:

```sh
dpkg --verify fleet-tools
exit
```

```text
??5??????   /usr/lib/fleet-tools/check-node
```

The `5` in the third column means the digest of the file differs from the package. A `?` means `dpkg` did not check that property. No output at all would mean every file matches.

## Record the result

Use your own names:

```sh
kubectl -n starfleet-031-050-03-02 create configmap repository-review \
  --from-literal=bad-package=fleet-tools_1.4.2_all.deb \
  --from-literal=changed-file=/usr/lib/fleet-tools/check-node
```

The grader verifies the chain again on the node, runs `dpkg --verify` itself and compares both findings with the ConfigMap.
