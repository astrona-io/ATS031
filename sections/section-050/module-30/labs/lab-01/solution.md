---
exam_objectives:
- Verify platform binaries before deploying
---
# Verify Detached GPG Signatures With gpgv: Solution

Connect to the lab first, so that `kubectl` talks to this lab's cluster and `$node_name` names its control plane node:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-03-01)"
node_name="astro-ats-031-lab-050-03-01-control-plane"
```

## Verify every document

`gpgv` takes the keyring with `--keyring`, then the signature, then the signed file. Write the keyring as `./publisher.gpg`: a name without a slash makes `gpgv` look for the file in its home directory, not in the current directory. Open a shell in the review directory and check all six documents, with the exit status after each one:

```sh
podman exec -it -w /var/lib/doc-review "$node_name" bash
for document in *.txt; do
  echo "== $document"
  gpgv --keyring ./publisher.gpg "$document.asc" "$document"; echo "exit $?"
done
exit
```

The documents, the keys and the damaged files are new on every start. One run printed this (shortened to four documents):

```text
== cargo-manifest.txt
gpgv: Signature made Tue Nov 17 19:54:17 2026 UTC
gpgv:                using RSA key D99766D0C49830B1A0577D7AC412CD41C6EA2D48
gpgv:                issuer "mirror@fleet.example"
gpgv: Can't check signature: No public key
exit 2
== comms-schedule.txt
gpgv: Signature made Tue Nov 17 19:54:17 2026 UTC
gpgv:                using RSA key 96D640D730B4C987E2C47A4ECC073574255C8545
gpgv:                issuer "publisher@fleet.example"
gpgv: Good signature from "Fleet Publisher <publisher@fleet.example>"
exit 0
== flight-plan.txt
gpgv: Signature made Tue Nov 17 19:54:17 2026 UTC
gpgv:                using RSA key 96D640D730B4C987E2C47A4ECC073574255C8545
gpgv:                issuer "publisher@fleet.example"
gpgv: BAD signature from "Fleet Publisher <publisher@fleet.example>"
exit 1
== nav-update.txt
gpgv: can't open 'nav-update.txt.asc': No such file or directory
gpgv: verify signatures failed: No such file or directory
exit 2
```

## Read the result

Only exit status `0` with `Good signature` counts. Each failure has its own reason:

- `BAD signature`: the publisher signed this document, but its content changed after signing.
- `Can't check signature: No public key`: a different key signed it. The `issuer` line is only a claim written inside the signature, so it never proves who signed.
- `can't open ... .asc`: there is no signature, so there is nothing to verify.

All three go into `rejected`. The fingerprint of the publisher key is the 40-character value on the `using RSA key` line of a good signature.

## Record the result

Use your own document names and fingerprint:

```sh
kubectl -n starfleet-031-050-03-01 create configmap signature-review \
  --from-literal=rejected="cargo-manifest.txt flight-plan.txt nav-update.txt" \
  --from-literal=fingerprint=96D640D730B4C987E2C47A4ECC073574255C8545
```

The grader runs `gpgv` on every document itself and compares the failures and the fingerprint with the ConfigMap.
