# Verify Detached GPG Signatures With gpgv — Solution

You solve this lab with one `gpgv` loop on the node and one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The node of a `kind` cluster is a container on your machine. Open a shell on the control plane node (write `docker` instead of `podman` if your machine uses Docker):

```sh
podman exec -it astro-ats-031-lab-050-03-01-control-plane bash
```

List the review directory:

```sh
cd /var/lib/doc-review
ls
```

It shows six `.txt` documents, `publisher.gpg` and an `.asc` signature for most documents. A document without an `.asc` file has nothing to verify.

## Step 2: verify every document (checks `rejected-files` and `accepted-files`)

`gpgv` takes the keyring with `--keyring`, then the signature, then the signed file. Write the keyring as `./publisher.gpg`: a name without a slash makes `gpgv` look for the file in its home directory, not in the current directory. Check all six documents, with the exit status after each one:

```sh
for document in *.txt; do
  echo "== $document"
  gpgv --keyring ./publisher.gpg "$document.asc" "$document"; echo "exit $?"
done
```

Only exit status `0` with `Good signature` counts. Each failure has its own reason:

- `BAD signature`: the publisher signed this document, but its content changed after signing.
- `Can't check signature: No public key`: a different key signed it. The `issuer` line is only a claim written inside the signature, so it never proves who signed.
- `can't open ... .asc`: there is no signature, so there is nothing to verify.

All three cases go into `rejected`. Every document that printed `Good signature` stays out of it.

## Step 3: read the publisher fingerprint (check `publisher-fingerprint`)

For a good signature, `gpgv` prints a line `using RSA key` followed by the 40-character fingerprint of the key that signed it. Print it for one document that passed. Replace `<GOOD_DOCUMENT>` with its name:

```sh
gpgv --keyring ./publisher.gpg <GOOD_DOCUMENT>.asc <GOOD_DOCUMENT> 2>&1 | grep 'using'
exit
```

`gpgv` writes its messages to standard error, so `2>&1` sends them to `grep`.

## Step 4: record the result (checks `rejected-files`, `accepted-files` and `publisher-fingerprint`)

Back on your machine, replace `<REJECTED_DOCUMENTS>` with the failing names from Step 2, separated by spaces, and `<FINGERPRINT>` with the value from Step 3. Save this as `configmap-signature-review.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: signature-review
  namespace: starfleet-031-050-03-01
data:
  rejected: "<REJECTED_DOCUMENTS>"
  fingerprint: "<FINGERPRINT>"
```

Apply it:

```sh
kubectl apply -f configmap-signature-review.yaml
```

## Step 5: test the record

Print both keys:

```sh
kubectl -n starfleet-031-050-03-01 get configmap signature-review -o jsonpath='{.data.rejected}{"\n"}{.data.fingerprint}{"\n"}'
```

The first line must show every document whose exit status was not `0` in Step 2, and no other. The second line must show the 40-character fingerprint from Step 3.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not leave out the document without an `.asc` file. A missing signature is a rejection, not a pass.
>
> Do not accept a document because its `issuer` line names the publisher. Only `Good signature` with exit status `0` proves that the publisher key signed it.
>
> Do not add a document that printed `Good signature` to `rejected`.
>
> Record the full 40-character fingerprint, not the short key ID. The grader ignores spaces and letter case, but not missing characters.
