# Verify The Running kubelet Against A Release Checksum

An audit found that the kubelet on the worker node `astro-ats-031-lab-050-02-05-worker` may not be the official build. The kubelet is the node agent that starts the containers of each Pod on a node. The worker holds the published digests in `/var/lib/kubelet-release/<version>/bin/linux/<architecture>/kubelet.sha256`, each file holding only the digest. Check the kubelet that actually runs and record the result in the ConfigMap `kubelet-review` in namespace `starfleet-031-050-02-05`.

1. Set the key `version` to the version of the running kubelet, for example `v1.35.0`, and the key `path` to the full path of the binary that the running kubelet process was started from.
2. Set the key `sha256` to the SHA-256 digest of that binary.
3. Set the key `result` to `match` if that digest equals the published digest for the version and the architecture of the worker, otherwise `mismatch`.

Do not restart the kubelet and do not change any file on the node; the path and the result are chosen at random each time the lab starts.
