# Verify Downloads With sha256sum --check

The directory `/var/lib/k8s-downloads` on the control plane node `astro-ats-031-lab-050-02-02-control-plane` holds `kubectl`, `kubeadm` and `kubelet`, each with the `.sha256` file that the release site publishes next to it. Each `.sha256` file holds only a 64-character digest, with no file name. Check all three downloads in one run of `sha256sum --check --strict` and record the result in the ConfigMap `download-check` in namespace `starfleet-031-050-02-02`.

1. Create `/var/lib/k8s-downloads/SHA256SUMS` in the format that `sha256sum --check` reads: one line per download, with the published digest, two spaces and the file name without a directory.
2. Run `sha256sum --check --strict SHA256SUMS` in that directory and set the key `exit-status` to its exit status, as a number.
3. Set the key `failed` to the name of the download that failed the check, or `none` if every download passed.

Take each digest from its `.sha256` file, never from the downloaded file, and do not change the downloads; each start of the lab decides at random whether one download is damaged.
