---
draft: true
---
# Rotate The Certificate Served By An Ingress

Solve this question on: `terminal`

Traefik serves `probe.example.test` using `probe-tls` in `rotation-training`. A replacement certificate and key are staged in `probe-next`, signed by the existing training CA. `probe-old` preserves the previous pair.

Allow about 10 minutes for task work. Cluster startup adds time.

## Tasks

1. Replace the certificate and key in the existing `probe-tls` Secret with the pair from `probe-next`. Keep the Ingress, host, CA and backend unchanged.
2. Establish a fresh TLS connection that verifies the CA and hostname.
3. Confirm its leaf certificate matches `probe-next`, differs from `probe-old`, and the application still responds successfully.

## Constraints

Do not disable certificate or hostname verification. Keep both staged Secrets and `rotation-trust` unchanged. Let the ingress controller reload the Secret; do not replace its certificate with a default certificate or change the route.

## How the answer is checked

The grader checks the active pair, then makes a new TLS connection with the CA from `rotation-trust`. It compares the served leaf certificate to the replacement and checks the original HTTP response. Merely updating a Secret is insufficient.
