# Verify And Create Blob Signatures With cosign — Solution

You solve this lab with `cosign` on the node and one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The node of a `kind` cluster is a container on your machine. Open a shell on the control plane node (write `docker` instead of `podman` if your machine uses Docker):

```sh
podman exec -it astro-ats-031-lab-050-03-03-control-plane bash
```

List both directories:

```sh
ls /var/lib/build-records /var/lib/approval
```

Most build records have a `.sig` file, and `/var/lib/approval` holds only `approval.txt`. A record without a `.sig` file has nothing to verify.

## Step 2: verify every build record (check `rejected-records`)

`cosign verify-blob` needs the public key, the signature and the file. By default it also looks for the signature in the public transparency log, which the node cannot reach. `--insecure-ignore-tlog=true` skips that lookup and checks only the signature against the key. Check all six records, with the exit status after each one:

```sh
cd /var/lib/build-records
for record in build-*.txt; do
  echo "== $record"
  cosign verify-blob --key fleet.pub --signature "$record.sig" --insecure-ignore-tlog=true "$record"; echo "exit $?"
done
```

A record that verifies prints `Verified OK` and exits with `0`. Every other record exits with a non-zero status. Three things make a record fail: its content changed after signing, another key signed it, or its `.sig` file is missing. All three go into `rejected`.

## Step 3: sign the approval (check `signed-approval`)

`cosign generate-key-pair` writes `cosign.key` and `cosign.pub` into the current directory. `COSIGN_PASSWORD=''` sets the empty password without a prompt. `--tlog-upload=false` signs without the transparency log, and `--yes` skips the confirmation prompt:

```sh
cd /var/lib/approval
COSIGN_PASSWORD='' cosign generate-key-pair
COSIGN_PASSWORD='' cosign sign-blob --yes --key cosign.key --tlog-upload=false --output-signature approval.txt.sig approval.txt
```

Verify the new signature with the new public key, the same way you checked the build records:

```sh
cosign verify-blob --key cosign.pub --signature approval.txt.sig --insecure-ignore-tlog=true approval.txt
```

It prints `Verified OK`.

## Step 4: delete the private key (check `private-key-removed`)

Whoever holds `cosign.key` can sign any file as you. The public key is all that others need to verify the approval:

```sh
rm cosign.key
ls
exit
```

`ls` shows `approval.txt`, `approval.txt.sig` and `cosign.pub`.

## Step 5: record the rejected records (check `rejected-records`)

Back on your machine, replace `<REJECTED_RECORDS>` with the failing names from Step 2, separated by spaces. Save this as `configmap-cosign-review.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cosign-review
  namespace: starfleet-031-050-03-03
data:
  rejected: "<REJECTED_RECORDS>"
```

Apply it:

```sh
kubectl apply -f configmap-cosign-review.yaml
```

## Step 6: test the record

Print the key:

```sh
kubectl -n starfleet-031-050-03-03 get configmap cosign-review -o jsonpath='{.data.rejected}{"\n"}'
```

It must show every record whose exit status was not `0` in Step 2, and no record that printed `Verified OK`.

## Step 7: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not leave out the record without a `.sig` file. A missing signature is a rejection, and `rejected` must list exactly the records that fail.
>
> Do not copy `fleet.pub` to `/var/lib/approval/cosign.pub`. The grader requires a new key pair.
>
> Do not change `approval.txt` before you sign it. The grader requires the original two lines.
>
> Do not delete `cosign.pub` with the private key. Without it, nobody can verify the approval, and both approval checks fail.
