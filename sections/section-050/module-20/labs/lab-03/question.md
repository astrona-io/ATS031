# Find The Binary That Fails Verification

The directory `/var/lib/node-bundle` on the control plane node `astro-ats-031-lab-050-02-03-control-plane` holds seven control plane binaries. Each binary has a file with the same name and the suffix `.sha256`, which holds only the published digest. One binary was changed after its digest was published; its size and its modification time did not change.

1. Create the ConfigMap `failing-binary` in namespace `starfleet-031-050-02-03` with the key `name`.
2. Set `name` to the bare file name of one staged binary, without a directory and without the `.sha256` suffix.
3. That binary must be the one whose digest differs from its published `.sha256` file.

Do not change or run the staged binaries; the changed binary is chosen at random each time the lab starts.
