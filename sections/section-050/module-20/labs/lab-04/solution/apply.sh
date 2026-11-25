#!/usr/bin/env bash
# Reference solution: compare each batch with the published index and with
# its shipped checksum, classify it and record the result.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-02-04}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-02-04}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
node_name="$cluster-control-plane"
index=/var/lib/release-index/release
incoming=/var/lib/k8s-incoming
node_architecture=$(kubectl get node "$node_name" -o jsonpath='{.status.nodeInfo.architecture}')
if [[ "$node_architecture" == amd64 ]]; then other_architecture=arm64; else other_architecture=amd64; fi
published_digest() { "$engine" exec "$node_name" cat "$index/$1/bin/linux/$2/kubectl.sha256"; }
expected_digest=$(published_digest v1.35.0 "$node_architecture")
other_arch_digest=$(published_digest v1.35.0 "$other_architecture")
old_version_digest=$(published_digest v1.34.4 "$node_architecture")
triage_values=()
for number in 1 2 3 4 5; do
  batch="batch-$number"
  actual_digest=$("$engine" exec "$node_name" sha256sum "$incoming/$batch/kubectl" | cut -d' ' -f1)
  shipped_digest=$("$engine" exec "$node_name" cat "$incoming/$batch/kubectl.sha256")
  if [[ "$actual_digest" == "$expected_digest" && "$shipped_digest" == "$expected_digest" ]]; then cause=ok
  elif [[ "$actual_digest" == "$expected_digest" ]]; then cause=stale-checksum
  elif [[ "$actual_digest" == "$other_arch_digest" ]]; then cause=wrong-arch
  elif [[ "$actual_digest" == "$old_version_digest" ]]; then cause=wrong-version
  else cause=tampered; rejected_batch="$batch"
  fi
  triage_values+=("--from-literal=$batch=$cause")
done
kubectl -n starfleet-031-050-02-04 create configmap download-triage \
  "${triage_values[@]}" --from-literal=rejected="$rejected_batch" \
  --dry-run=client -o yaml | kubectl apply -f -
