#!/usr/bin/env bash
# Reference solution: verify every build record with the fleet key, record
# the failures, then sign approval.txt with a new key pair and delete the
# private key.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-03-03}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-03-03}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
node_name="$cluster-control-plane"
rejected=()
for record in $("$engine" exec -w /var/lib/build-records "$node_name" find . -maxdepth 1 -name 'build-*.txt' -printf '%f\n' | sort); do
  if ! "$engine" exec -w /var/lib/build-records "$node_name" cosign verify-blob --key fleet.pub \
      --signature "$record.sig" --insecure-ignore-tlog=true "$record" >/dev/null 2>&1; then
    rejected+=("$record")
  fi
done
kubectl -n starfleet-031-050-03-03 create configmap cosign-review --from-literal=rejected="${rejected[*]}" \
  --dry-run=client -o yaml | kubectl apply -f -
"$engine" exec -w /var/lib/approval -e COSIGN_PASSWORD= "$node_name" cosign generate-key-pair
"$engine" exec -w /var/lib/approval -e COSIGN_PASSWORD= "$node_name" cosign sign-blob --yes --key cosign.key \
  --tlog-upload=false --output-signature approval.txt.sig approval.txt
"$engine" exec -w /var/lib/approval "$node_name" rm cosign.key
