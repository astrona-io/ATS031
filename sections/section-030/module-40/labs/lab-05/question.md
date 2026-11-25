---
exam_objectives:
- Properly set up Ingress with TLS
---
# Rotate An Expiring Certificate

Allow about 8 minutes for the tasks.

The certificate of `orbit.example.test` expires in two days. Replace it before clients start to fail, without a gap in service and without changing the Ingress.

## Starting state

The namespace `starfleet-031-030-04-05` holds the Service `orbit`, the Ingress `orbit` and the Secret `orbit-tls`. The Ingress serves `orbit.example.test` over HTTPS with that Secret. The certificate in `orbit-tls` is valid for two days. The ConfigMap `orbit-previous` keeps a copy of the old certificate for the grader; do not change it.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-04-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-04-05" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Create a new private key and a new self-signed certificate for `orbit.example.test` with `DNS:orbit.example.test` in its Subject Alternative Name (SAN), valid for 90 days. Replace the data of the existing Secret `orbit-tls` in place, so the Ingress keeps the same Secret name. Traefik must then serve the new certificate.

## Verify the result

The grader compares the certificate in `orbit-tls` with the old copy and checks the new key, the SAN and the remaining validity. It then connects from a pod with the server name `orbit.example.test` and compares the served certificate with the Secret.
