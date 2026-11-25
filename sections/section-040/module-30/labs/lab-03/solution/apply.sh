#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-040-03-03}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cat <<'EOF' | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: image-scanner
  namespace: dock-031-040-03-03
  labels:
    app: image-scanner
spec:
  replicas: 1
  selector:
    matchLabels:
      app: image-scanner
  template:
    metadata:
      labels:
        app: image-scanner
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      containers:
      - name: scanner
        image: docker.io/curlimages/curl:8.11.1
        command:
        - sleep
        - '86400'
        securityContext:
          allowPrivilegeEscalation: false
        volumeMounts:
        - name: scratch
          mountPath: /scratch
        - name: settings
          mountPath: /etc/scanner
          readOnly: true
      volumes:
      - name: scratch
        emptyDir: {}
      - name: settings
        configMap:
          name: scanner-settings
EOF
kubectl -n dock-031-040-03-03 rollout status deployment/image-scanner --timeout=180s
