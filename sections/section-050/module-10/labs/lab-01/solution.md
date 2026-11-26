# Find The Files That Fail A Checksum Manifest — Solution

You solve this lab with two `sha256sum` commands on the node and one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The node of a `kind` cluster is a container on your machine. Open a shell on the control plane node (write `docker` instead of `podman` if your machine uses Docker):

```sh
podman exec -it astro-ats-031-lab-050-01-01-control-plane bash
```

List the release directory and read the manifest:

```sh
cd /var/lib/fleet-release
ls -l
cat SHA256SUMS
```

The six files all have normal sizes and the same modification time. A change of one byte keeps the size, and `touch` can set any time, so `ls -l` cannot show which files changed. Only a digest of the content shows it.

## Step 2: find every failing file (checks `failed-files` and `passing-files`)

`sha256sum --check` reads each line of the manifest, computes the digest of the named file and prints `OK` or `FAILED` after the file name. The names in the manifest have no directory, so run the check inside the release directory. The option `--quiet` prints only the lines that fail:

```sh
sha256sum --check --quiet SHA256SUMS; echo "exit status $?"
```

Each failing file prints one line that ends with `: FAILED`, and `sha256sum` ends with a warning that counts them. The exit status is `1`, because at least one file failed. The files that do not appear here passed the check, so they must stay out of your list.

## Step 3: compute the digest of fleet-agent (check `agent-digest`)

`sha256sum` without `--check` prints the digest of a file, two spaces and its name. Keep only the digest:

```sh
sha256sum fleet-agent | cut -d' ' -f1
exit
```

The digest is 64 lowercase hexadecimal characters. You need the current digest, even when `fleet-agent` failed the check in Step 2.

## Step 4: record the result (checks `failed-files`, `passing-files` and `agent-digest`)

Back on your machine, write the ConfigMap. Replace `<FAILED_FILES>` with the failing names from Step 2, separated by commas, and `<AGENT_DIGEST>` with the digest from Step 3. Save this as `configmap-manifest-check.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: manifest-check
  namespace: starfleet-031-050-01-01
data:
  failed: "<FAILED_FILES>"
  agent-sha256: "<AGENT_DIGEST>"
```

Apply it:

```sh
kubectl apply -f configmap-manifest-check.yaml
```

The quotes keep every value a string, which is the only type a ConfigMap stores.

## Step 5: test the record

Print both keys:

```sh
kubectl -n starfleet-031-050-01-01 get configmap manifest-check -o jsonpath='{.data.failed}{"\n"}{.data.agent-sha256}{"\n"}'
```

The first line must show exactly the names that printed `FAILED` in Step 2. The second line must show the digest from Step 3.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not list all six files to be safe. A file that passes the manifest must not appear in `failed`.
>
> Do not leave out a failing file. Between one and three files fail, so read every `FAILED` line.
>
> Do not record the digest from `SHA256SUMS` for `fleet-agent`. The task asks for the digest of the file as it is now, which differs from the manifest when `fleet-agent` failed.
>
> Do not change a file or the manifest to make the check pass. The grader compares them with the staged copies and fails every check when they differ.
