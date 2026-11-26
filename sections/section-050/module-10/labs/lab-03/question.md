# Install A Verified Binary Into A Protected Directory

On the control plane node `astro-ats-031-lab-050-01-03-control-plane`, three download caches `/var/cache/fleet/cache-1`, `cache-2` and `cache-3` each hold a copy of `fleet-agent`. `/var/lib/fleet-release` holds `publisher.pub`, `SHA256SUMS` and `SHA256SUMS.sig`, a signature made with `openssl dgst -sha256 -sign`. Only one cache copy matches the authenticated manifest. An unverified copy is already installed in `/opt/fleet/bin`, a directory that any user can write.

1. Make `/opt/fleet` and `/opt/fleet/bin` owned by `root` and not writable by group or others.
2. Verify `SHA256SUMS` with `publisher.pub`, find the cache whose `fleet-agent` matches it, and install that copy as `/opt/fleet/bin/fleet-agent`, owned by `root:root` with mode `0755`.
3. Create the ConfigMap `install-record` in namespace `starfleet-031-050-01-03` with the key `cache`, the name of the cache that held the genuine copy (for example `cache-2`), and the key `sha256`, the digest from the authenticated manifest.

Do not run any `fleet-agent` copy and do not change the files in `/var/lib/fleet-release` or the caches; the genuine cache is chosen at random each time the lab starts.
