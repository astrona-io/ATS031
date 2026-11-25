---
exam_objectives:
- Properly set up Ingress with TLS
---
# Sign A Server Certificate With A Lab CA

Allow about 10 minutes for the tasks.

The relay team uses an internal certificate authority (CA) for its test services. Clients trust only that CA, not single server certificates. Sign a server certificate for `relay.example.test` with the CA and serve it.

## Starting state

The namespace `starfleet-031-030-03-04` holds the Deployment `relay`, the Service `relay` on port 80 and the Ingress `relay`. The Ingress routes `relay.example.test` on the `websecure` entrypoint and names the Secret `relay-tls`, which does not exist. The Secret `lab-ca` of type `kubernetes.io/tls` holds the CA certificate in `tls.crt` and the CA private key in `tls.key`. The ConfigMap `lab-ca-original` keeps a copy of the CA certificate for the grader; do not change it.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-03-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-03-04" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Create a new private key and a certificate signing request (CSR) for `relay.example.test`. Sign it with the CA from the Secret `lab-ca`, for 30 days, so that the signed certificate has `DNS:relay.example.test` in its Subject Alternative Name (SAN). Store the signed certificate and its key as the Secret `relay-tls` of type `kubernetes.io/tls` in `starfleet-031-030-03-04`. Do not change the Ingress or the Secret `lab-ca`.

## Verify the result

The grader decodes your certificate and the CA certificate. It checks that the issuer of your certificate is the CA, the SAN and the key. It then connects from a pod with the CA certificate as the only trusted certificate and expects a verified HTTPS response from `relay`.
