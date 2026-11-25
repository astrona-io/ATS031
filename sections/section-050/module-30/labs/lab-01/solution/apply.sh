#!/usr/bin/env bash
# Reference solution: verify every document with gpgv and the publisher
# keyring, collect the ones without a good signature, read the fingerprint of
# the publisher key from a good signature and record the result.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-03-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-03-01}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
node_name="$cluster-control-plane"
review_directory=/var/lib/doc-review
rejected_documents=()
for document in flight-plan.txt crew-roster.txt fuel-report.txt nav-update.txt comms-schedule.txt cargo-manifest.txt; do
  if gpgv_output=$("$engine" exec -w "$review_directory" "$node_name" gpgv --keyring ./publisher.gpg "$document.asc" "$document" 2>&1); then
    publisher_fingerprint=$(printf '%s\n' "$gpgv_output" | sed -n 's/.*using [A-Za-z0-9]* key \([0-9A-F]\{40\}\).*/\1/p')
  else
    rejected_documents+=("$document")
  fi
done
kubectl -n starfleet-031-050-03-01 create configmap signature-review \
  --from-literal=rejected="${rejected_documents[*]}" --from-literal=fingerprint="$publisher_fingerprint" \
  --dry-run=client -o yaml | kubectl apply -f -
