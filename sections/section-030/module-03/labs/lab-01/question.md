---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Publish Scout Over HTTPS With Your Own Certificate

Solve this question on: `terminal`

The scout team needs its application on `scout.example.test` over HTTPS. The cluster runs the Traefik Ingress controller with the entrypoints `web` (HTTP) and `websecure` (HTTPS). The namespace `starfleet-031-030-03-01` holds a working `scout` Deployment and the Service `scout` on port 80. There is no Secret and no Ingress for `scout`, and no certificate exists yet.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-03-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

Allow about 8 minutes for task work. Cluster startup adds time.

## Tasks

1. Create a self-signed certificate and key for `scout.example.test`, with that name in the Subject Alternative Name (SAN), the certificate field that lists the names it is valid for.
2. Store the certificate and key as the Secret `scout-tls` of type `kubernetes.io/tls` in `starfleet-031-030-03-01`.
3. Create the Ingress `scout` in `starfleet-031-030-03-01` for class `traefik`, with the host `scout.example.test`, a `Prefix` path `/` to the Service `scout` on port 80, the `websecure` entrypoint, TLS enabled on the router, and `scout-tls` in `spec.tls`.
4. Prove the result. A client that trusts your certificate must get the `scout` response from `https://scout.example.test`, and must reject the connection for a wrong server name.

## Constraints

- Keep the `scout` Deployment and the Service `scout` unchanged.

## How the answer is checked

The grader runs three checks. The first needs the Secret `scout-tls` of type `kubernetes.io/tls` in `starfleet-031-030-03-01`. The second reads the Ingress `scout` and needs class `traefik`. The third runs from inside the `probe` pod. It connects to the Traefik Service on port 443 with the certificate in `scout-tls` as its only trusted certificate. `https://scout.example.test` must answer 200 from the Service `scout`, and a handshake for the server name `wrong.example.test` must be rejected. Every check also needs the `scout` Deployment fully rolled out and the Service `scout` in place.

Hint: `openssl req -x509 -newkey rsa:2048 -nodes -subj '/CN=scout.example.test' -addext 'subjectAltName=DNS:scout.example.test'` creates a certificate with the name in its SAN.
