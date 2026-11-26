# Verify A Signed apt Repository And An Installed Package

The control plane node `astro-ats-031-lab-050-03-02-control-plane` has a local copy of the fleet apt repository in `/var/lib/fleet-apt`: the signed `Release` file with its detached signature `Release.gpg`, the package index `Packages`, the package files in `pool/`, and `fleet-archive.gpg`, a keyring with the public key of the archive. The package `fleet-tools` from this repository is installed on the node. Follow the chain of trust from `Release` down to each package file, then check the installed files, and record the result in the ConfigMap `repository-review` in namespace `starfleet-031-050-03-02`.

1. Create the ConfigMap with the key `bad-package`, set to the file name of one package listed in `Packages`, and the key `changed-file`, set to the full path of one file that `fleet-tools` installed.
2. `bad-package` must name the package file whose SHA-256 digest differs from its `SHA256:` field in `Packages`, for example `fleet-agent_2.0.1_all.deb`, after you have verified `Release.gpg` with `gpgv` and the digest of `Packages` against `Release`.
3. `changed-file` must be the installed `fleet-tools` file that `dpkg` reports as changed.

Do not change the repository, and do not reinstall or remove any package; the damaged package and the changed file are chosen at random each time the lab starts.
