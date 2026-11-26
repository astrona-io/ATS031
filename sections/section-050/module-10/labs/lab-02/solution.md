# Verify A Signed Checksum Manifest — Solution

You solve this lab with `openssl` and `sha256sum` on the node and one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The node of a `kind` cluster is a container on your machine. Open a shell on the control plane node (write `docker` instead of `podman` if your machine uses Docker):

```sh
podman exec -it astro-ats-031-lab-050-01-02-control-plane bash
```

List the release directory:

```sh
cd /var/lib/relay-release
ls -l . mirror-a mirror-b mirror-c
```

Each mirror has the same three files. One mirror is genuine, one has a manifest signed with another key, and one has a binary that changed after the publisher signed the manifest. Nothing in the listing shows which is which.

## Step 2: verify the signature of each manifest (check `signed-mirror`)

`openssl dgst -sha256 -verify` takes the public key, the signature file and the signed file. It prints `Verified OK` and exits with `0` when the matching private key signed exactly these bytes. Otherwise it prints `Verification failure` and exits with `1`. Run it for each mirror:

```sh
for mirror in a b c; do
  echo "== mirror-$mirror"
  openssl dgst -sha256 -verify publisher.pub -signature mirror-$mirror/SHA256SUMS.sig mirror-$mirror/SHA256SUMS
done
```

Two mirrors print `Verified OK`. The third was signed with another key. Its binary and its manifest still agree with each other, which is exactly why a checksum alone proves nothing about the publisher.

## Step 3: check the binary against the signed manifests (check `trusted-mirror`)

Only a manifest with a good signature is worth a comparison. The names in `SHA256SUMS` have no directory, so run the check inside each mirror folder:

```sh
for mirror in a b c; do
  echo "== mirror-$mirror"
  (cd mirror-$mirror && sha256sum --check SHA256SUMS)
done
```

On one of the two signed mirrors, `relay-agent` reports `FAILED`: the publisher signed the manifest, but the binary changed after that. The mirror with `Verified OK` in Step 2 and `relay-agent: OK` here is the genuine release.

## Step 4: read the trusted digest (check `review-digest`)

Read the digest from the manifest of that mirror. Replace `<MIRROR>` with its letter:

```sh
cut -d' ' -f1 mirror-<MIRROR>/SHA256SUMS
exit
```

The digest comes from the signed manifest, so you trust it because of the signature, not because it matches a file you downloaded.

## Step 5: record the result (checks `signed-mirror`, `trusted-mirror` and `review-digest`)

Back on your machine, replace `<MIRROR>` with the letter and `<DIGEST>` with the digest from Step 4. Save this as `configmap-artifact-review.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: artifact-review
  namespace: starfleet-031-050-01-02
data:
  mirror: "<MIRROR>"
  sha256: "<DIGEST>"
```

Apply it:

```sh
kubectl apply -f configmap-artifact-review.yaml
```

## Step 6: test the record

Print both keys:

```sh
kubectl -n starfleet-031-050-01-02 get configmap artifact-review -o jsonpath='{.data.mirror}{"\n"}{.data.sha256}{"\n"}'
```

The first line must show the letter of the mirror that passed both checks. The second line must show the digest from Step 4.

## Step 7: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not pick a mirror only because `sha256sum --check` prints `OK`. The mirror signed with another key passes that check too, and fails the signature check.
>
> Do not pick a mirror only because its signature verifies. The altered mirror has a good signature, but its `relay-agent` fails the manifest.
>
> Write only the letter in `mirror`, such as `b`. The grader also accepts `mirror-b`, but nothing else.
>
> Do not compute `sha256` from `relay-agent` on a mirror that failed. Take it from the signed `SHA256SUMS` of the genuine mirror.
