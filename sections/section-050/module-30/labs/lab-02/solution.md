# Verify A Signed apt Repository And An Installed Package — Solution

You solve this lab by checking each link of the chain of trust on the node and recording two findings in one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The node of a `kind` cluster is a container on your machine. Open a shell on the control plane node (write `docker` instead of `podman` if your machine uses Docker):

```sh
podman exec -it astro-ats-031-lab-050-03-02-control-plane bash
```

List the repository and read the end of `Release`:

```sh
cd /var/lib/fleet-apt
ls -R
tail -n 2 Release
```

The chain has three links. The signature proves `Release`. `Release` holds the digest of `Packages`. `Packages` holds the digest of each file in `pool/`. A link proves something only when the link above it was proven first.

## Step 2: verify the signature of Release

Write the keyring as `./fleet-archive.gpg`, so `gpgv` reads the file in the current directory:

```sh
gpgv --keyring ./fleet-archive.gpg Release.gpg Release
```

`gpgv` prints `Good signature` and exits with `0`. `Release` is now trusted.

## Step 3: check Packages against Release

The last line of `Release` is a space, the digest, the size and the name `Packages`. The `sed` command prints only the digest. The `printf` turns it into a line in the check format:

```sh
printf '%s  Packages\n' "$(sed -n 's/^ \([0-9a-f]\{64\}\) [0-9]* Packages$/\1/p' Release)" | sha256sum --check
```

It prints `Packages: OK`. `Packages` is now trusted too, and so is every `SHA256:` field in it.

## Step 4: check every package file (checks `review-record` and `bad-package`)

Each stanza of `Packages` has a `Filename:` line before its `SHA256:` line. `awk` remembers the file name and prints a check line when it reaches the digest:

```sh
awk '/^Filename:/ {file=$2} /^SHA256:/ {print $2 "  " file}' Packages | sha256sum --check
```

Three lines end with `OK`. One line, such as `pool/fleet-probe_0.9.7_all.deb: FAILED`, names the damaged package. Record only the file name after `pool/`.

## Step 5: check the installed files (checks `review-record` and `changed-file`)

`dpkg --verify` compares every installed file of a package with the MD5 digest that the package shipped. It prints a line only for a file that differs:

```sh
dpkg --verify fleet-tools
exit
```

The line starts with a column of check flags and ends with the path. A `5` as the third character means the digest of the file differs. That path, under `/usr/lib/fleet-tools/`, is the changed file. The file has the same modification time as before, so only the digest shows the change.

## Step 6: record the result (checks `review-record`, `bad-package` and `changed-file`)

Back on your machine, replace `<PACKAGE_FILE>` with the name from Step 4 and `<CHANGED_FILE>` with the path from Step 5. Save this as `configmap-repository-review.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: repository-review
  namespace: starfleet-031-050-03-02
data:
  bad-package: "<PACKAGE_FILE>"
  changed-file: "<CHANGED_FILE>"
```

Apply it:

```sh
kubectl apply -f configmap-repository-review.yaml
```

## Step 7: test the record

Print both keys:

```sh
kubectl -n starfleet-031-050-03-02 get configmap repository-review -o jsonpath='{.data.bad-package}{"\n"}{.data.changed-file}{"\n"}'
```

The first line must show the `.deb` name from the `FAILED` line of Step 4. The second line must show the path that `dpkg --verify` printed in Step 5.

## Step 8: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not compare a package file with a digest you computed yourself or with a value from outside `Packages`. Only the `SHA256:` fields in the signed chain count.
>
> Write `changed-file` as the full path that `dpkg --verify` prints, starting with `/usr/lib/fleet-tools/`. A bare file name fails the check.
>
> Do not reinstall `fleet-tools` or change a file in the repository. The grader then finds no changed file or no damaged package and fails every check.
