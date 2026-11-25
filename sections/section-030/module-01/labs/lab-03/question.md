---
exam_objectives:
- Properly set up Ingress with TLS
---
# Create A TLS Secret From A Certificate And Key

Allow about 8 minutes for the tasks.

The vault team has an Ingress for `vault.local` that already names the Secret `vault-tls`, but the Secret does not exist. Traefik therefore serves its own default certificate. Create the certificate, the key and the Secret.

## Starting state

The namespace `starfleet-031-030-01-03` holds the Deployment `vault`, the Service `vault` on port 80 and the Ingress `vault`. The Ingress uses the `websecure` entrypoint and has a `tls` entry for `vault.local` with the Secret name `vault-tls`. The Secret `vault-tls` does not exist.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-01-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-01-03" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Create a self-signed certificate and its private key for `vault.local`. The certificate must have `DNS:vault.local` in its Subject Alternative Name (SAN) and must be valid for 90 days. Store the pair as the Secret `vault-tls` of type `kubernetes.io/tls` in `starfleet-031-030-01-03`, with the keys `tls.crt` and `tls.key`. Do not change the Ingress.

## Verify the result

The grader reads the Secret and checks that the key belongs to the certificate, the SAN and the remaining validity. It then connects to Traefik from a pod with the server name `vault.local`. It compares the certificate that Traefik sends with the one in your Secret and checks the HTTPS response from `vault`.
