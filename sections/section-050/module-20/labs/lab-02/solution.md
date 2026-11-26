# Verify Downloads With sha256sum --check — Solution

You solve this lab with one check file on the node and one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The node of a `kind` cluster is a container on your machine. Open a shell on the control plane node (write `docker` instead of `podman` if your machine uses Docker):

```sh
podman exec -it astro-ats-031-lab-050-02-02-control-plane bash
```

List the downloads and print one published digest:

```sh
cd /var/lib/k8s-downloads
ls -l
cat kubectl.sha256; echo
```

The directory has the three binaries and their `.sha256` files, and no `SHA256SUMS` yet. A `.sha256` file holds only the digest, so `sha256sum --check` cannot read it as it is.

## Step 2: build the check file (check `check-file`)

`sha256sum --check` needs one line per file: the digest, two spaces and the file name. The loop writes that line for each download, with the digest read from the published `.sha256` file:

```sh
for tool in kubectl kubeadm kubelet; do
  printf '%s  %s\n' "$(cat $tool.sha256)" "$tool"
done > SHA256SUMS
cat SHA256SUMS
```

The loop never runs `sha256sum` on a download. A digest computed from the file you want to check always matches that file, so it proves nothing.

## Step 3: run the strict check (check `check-result`)

`--strict` makes `sha256sum` fail on any line that is not in the check format, so a broken line cannot be skipped in silence. Print the exit status right after the check:

```sh
sha256sum --check --strict SHA256SUMS; echo "exit status $?"
```

When every file matches, each line ends with `OK` and the exit status is `0`. When one file was changed, its line ends with `FAILED`, `sha256sum` prints a warning that one computed checksum did not match, and the exit status is `1`.

## Step 4: find the failing download (check `failed-download`)

Read the name on the `FAILED` line of Step 3. If no line says `FAILED`, the answer is `none`. Then leave the node:

```sh
exit
```

## Step 5: record the result (checks `check-result` and `failed-download`)

Back on your machine, replace `<EXIT_STATUS>` with `0` or `1` and `<FAILED>` with the failing name or `none`. Save this as `configmap-download-check.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: download-check
  namespace: starfleet-031-050-02-02
data:
  exit-status: "<EXIT_STATUS>"
  failed: "<FAILED>"
```

Apply it:

```sh
kubectl apply -f configmap-download-check.yaml
```

Keep the quotes around the exit status. A ConfigMap stores only strings, and the API server rejects an unquoted number.

## Step 6: test the record

Print both keys:

```sh
kubectl -n starfleet-031-050-02-02 get configmap download-check -o jsonpath='{.data.exit-status}{"\n"}{.data.failed}{"\n"}'
```

The first line must show the exit status from Step 3. The second line must show the `FAILED` name, or `none` when every line ended with `OK`.

## Step 7: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not build `SHA256SUMS` with `sha256sum kubectl kubeadm kubelet`. Those digests come from the downloads themselves, and the grader requires the digests from the `.sha256` files.
>
> Write the file name without a directory and with exactly two spaces after the digest. The grader rejects any other line format.
>
> Do not record `failed` as empty when every download passes. Write `none`.
>
> Do not change a download or a `.sha256` file. The grader compares them with the staged copies and fails every check when they differ.
