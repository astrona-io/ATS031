#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-040-02-03}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
# The same corrected policy for all three namespaces: select every pod, allow
# all egress except the metadata address.
for namespace in starfleet-031-040-02-03 outpost-031-040-02-03 dock-031-040-02-03; do
  cat <<EOF | kubectl replace -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: metadata-guard
  namespace: $namespace
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 169.254.169.254/32
EOF
done
