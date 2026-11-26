# Pick The Release Files For A Node

An offline mirror of the Kubernetes release site is in `/var/lib/k8s-mirror` on the control plane node `astro-ats-031-lab-050-02-01-control-plane`. It uses the layout `release/<version>/bin/<os>/<architecture>/<name>`, with a `<name>.sha256` file next to each binary. Record the `kubeadm` file to install on the worker node `astro-ats-031-lab-050-02-01-worker` in the ConfigMap `release-pick` in namespace `starfleet-031-050-02-01`.

1. Set the key `path` to `release/<version>/bin/linux/<architecture>/kubeadm`, relative to the mirror, where `<version>` is the current stable version that the mirror publishes.
2. In that path, `<architecture>` must be the CPU architecture of the worker node, in the form the release paths use (`amd64` or `arm64`).
3. Set the key `sha256` to the published digest of that file, from its `.sha256` file.

Do not change the mirror; the stable version is chosen at random each time the lab starts.
