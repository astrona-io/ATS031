---
exam_objectives:
- Verify platform binaries before deploying
---
# Verify And Create Blob Signatures With cosign: Solution

Connect to the lab first, so that `kubectl` talks to this lab's cluster and `$node_name` names its control plane node. Then open a shell inside the node:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-03-03)"
node_name="astro-ats-031-lab-050-03-03-control-plane"
podman exec -it "$node_name" bash
```

The keys and the damaged records are new on every start. The output below comes from one run.

## Verify every build record

`cosign verify-blob` takes the public key with `--key`, the signature with `--signature` and the blob as the last argument. It computes the digest of the blob and checks the signature against it. `--insecure-ignore-tlog=true` skips the lookup in the Rekor transparency log, which the node cannot reach. Check all six records, with the exit status after each:

```sh
cd /var/lib/build-records
for record in build-*.txt; do
  echo "== $record"
  cosign verify-blob --key fleet.pub --signature "$record.sig" --insecure-ignore-tlog=true "$record"; echo "exit $?"
done
```

```text
== build-agent.txt
WARNING: Skipping tlog verification is an insecure practice that lacks of transparency and auditability verification for the blob.
Verified OK
exit 0
== build-probe.txt
WARNING: Skipping tlog verification is an insecure practice that lacks of transparency and auditability verification for the blob.
Error: invalid signature when validating ASN.1 encoded signature
main.go:74: error during command execution: invalid signature when validating ASN.1 encoded signature
exit 1
== build-scheduler.txt
WARNING: Skipping tlog verification is an insecure practice that lacks of transparency and auditability verification for the blob.
Error: ecdsa: Invalid IEEE_P1363 encoded bytes
main.go:74: error during command execution: ecdsa: Invalid IEEE_P1363 encoded bytes
exit 1
```

The output is shortened to three of the six records. Only `Verified OK` with exit status `0` counts. The `WARNING` line comes from the skipped log check and appears for every record.

The error text does not tell you the reason. `invalid signature` appears both when the record changed after signing and when another key signed it. In this run `build-scheduler.txt` has no `.sig` file at all, and cosign reports the empty signature as `Invalid IEEE_P1363 encoded bytes`. Run `ls` to spot a missing signature. All three cases go into `rejected`.

## Sign the approval with a new key

`cosign generate-key-pair` writes `cosign.key` (the private key, encrypted with a password) and `cosign.pub` (the public key) into the current directory. An empty `COSIGN_PASSWORD` skips the password question. That is acceptable for a lab key and never for a real one:

```sh
cd /var/lib/approval
COSIGN_PASSWORD='' cosign generate-key-pair
COSIGN_PASSWORD='' cosign sign-blob --yes --key cosign.key --tlog-upload=false --output-signature approval.txt.sig approval.txt
```

```text
Private key written to cosign.key
Public key written to cosign.pub
Using payload from: approval.txt
Wrote signature to file approval.txt.sig
```

`--tlog-upload=false` stops cosign from sending the signing event to Rekor. Check the new signature, then delete the private key, so that nobody else on the node can sign with it:

```sh
cosign verify-blob --key cosign.pub --signature approval.txt.sig --insecure-ignore-tlog=true approval.txt
rm cosign.key
ls
exit
```

```text
WARNING: Skipping tlog verification is an insecure practice that lacks of transparency and auditability verification for the blob.
Verified OK
approval.txt
approval.txt.sig
cosign.pub
```

## Record the result

Use your own record names:

```sh
kubectl -n starfleet-031-050-03-03 create configmap cosign-review \
  --from-literal=rejected="build-probe.txt build-relay.txt build-scheduler.txt"
```

The grader verifies every build record with `fleet.pub` itself, then verifies `approval.txt.sig` with your `cosign.pub` and checks that `cosign.key` is gone.
