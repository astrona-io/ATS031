# Find The Files That Fail A Checksum Manifest

The fleet build team copied six release files to `/var/lib/fleet-release` on the control plane node `astro-ats-031-lab-050-01-01-control-plane`. The directory also holds a `SHA256SUMS` manifest with one line per file (digest, two spaces, file name), and the manifest is correct. Some files changed during the copy. Record your findings in the ConfigMap `manifest-check` in namespace `starfleet-031-050-01-01`.

1. Set the key `failed` to the names of every file that fails the check against `SHA256SUMS`, separated by commas, for example `fleet-cli,fleet-sync`.
2. Make sure `failed` names no file that passes the check.
3. Set the key `agent-sha256` to the current 64-character SHA-256 digest of `fleet-agent`, whether it passes or fails.

Do not change the files or the manifest; the failing files are chosen at random each time the lab starts.
