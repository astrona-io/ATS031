#!/usr/bin/env bash
# Reference solution: turn the digest-only .sha256 files into one SHA256SUMS
# file in the check format, run the strict check and record the result.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-02-02}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-02-02}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
node_name="$cluster-control-plane"
downloads=/var/lib/k8s-downloads
checksum_lines=""
for tool in kubectl kubeadm kubelet; do
  published_digest=$("$engine" exec "$node_name" cat "$downloads/$tool.sha256")
  checksum_lines+="$published_digest  $tool"$'\n'
done
printf '%s' "$checksum_lines" | "$engine" exec -i "$node_name" tee "$downloads/SHA256SUMS" >/dev/null
set +e
check_output=$("$engine" exec -w "$downloads" "$node_name" sha256sum --check --strict SHA256SUMS 2>/dev/null)
exit_status=$?
set -e
failed_file=$(printf '%s\n' "$check_output" | grep ': FAILED$' | cut -d: -f1 || true)
kubectl -n starfleet-031-050-02-02 create configmap download-check \
  --from-literal=exit-status="$exit_status" --from-literal=failed="${failed_file:-none}" \
  --dry-run=client -o yaml | kubectl apply -f -
