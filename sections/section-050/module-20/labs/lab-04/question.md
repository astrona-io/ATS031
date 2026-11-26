# Classify Why Each Download Fails

Five download jobs fetched `kubectl` to the control plane node `astro-ats-031-lab-050-02-04-control-plane`. Each of `/var/lib/k8s-incoming/batch-1` to `batch-5` holds the downloaded `kubectl`, the `kubectl.sha256` file the job saved with it, and a `SOURCE` file with the requested release path. The trusted published digests are in `/var/lib/release-index/release/<version>/bin/linux/<architecture>/kubectl.sha256`, for `v1.34.4` and `v1.35.0`, `amd64` and `arm64`. Record one cause per batch in the ConfigMap `download-triage` in namespace `starfleet-031-050-02-04`, with the keys `batch-1` to `batch-5`.

1. Mark the batch whose file and saved checksum both match the published digest for the requested path as `ok`, and the batch whose file matches but whose saved checksum does not as `stale-checksum`.
2. Mark the batch that holds the requested version for the other architecture as `wrong-arch`, the batch that holds the other version for the requested architecture as `wrong-version`, and the batch whose file matches no published digest as `tampered`.
3. Set the key `rejected` to the name of the tampered batch, for example `batch-3`.

Do not run or change the downloaded files; each cause appears exactly once, in a random order each time the lab starts.
