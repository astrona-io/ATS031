---
exam_objectives:
- Properly set up Ingress with TLS
---
# Create A Self-Signed Certificate For Two Names

Allow about 8 minutes for the tasks.

The depot site answers on two names, `depot.example.test` and `www.depot.example.test`. The Ingress is ready, but the certificate is missing. Create one self-signed certificate that is valid for both names.

## Starting state

The namespace `starfleet-031-030-03-03` holds the Deployment `depot`, the Service `depot` on port 80 and the Ingress `depot`. The Ingress routes both names on the `websecure` entrypoint and has one `tls` entry for both names with the Secret name `depot-tls`. The Secret does not exist.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-03-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-03-03" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Create one self-signed certificate and its private key. The Subject Alternative Name (SAN) must list `DNS:depot.example.test` and `DNS:www.depot.example.test`, and the certificate must be valid for 30 days. Store the pair as the Secret `depot-tls` of type `kubernetes.io/tls` in `starfleet-031-030-03-03`. Do not change the Ingress.

## Verify the result

The grader decodes the certificate in the Secret and checks that it is self-signed, the two names, the validity and the key. It then connects from a pod with each server name and checks that Traefik sends this certificate and that a client that trusts it gets the `depot` response.
