---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Verify TLS Termination And Server Identity

Solve this question on: `terminal`

The namespace `starfleet-031-030-01-01` runs the healthy `probe` Deployment behind the Service `probe` on port 80. The Traefik Ingress controller, the component that receives HTTP and HTTPS requests and sends them to Services, runs in `ingress-system` with the IngressClass `traefik` and the HTTPS entrypoint `websecure`. The TLS Secret `probe-tls` in `starfleet-031-030-01-01` holds a certificate and key for `probe.local`. No Ingress exists yet.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-01-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

Allow about 6 minutes for task work. Cluster startup adds time.

## Tasks

1. Look at the Secret `probe-tls` and the Service `probe` in `starfleet-031-030-01-01`.
2. Create the Ingress `probe` in `starfleet-031-030-01-01` for class `traefik`. It has the host `probe.local`, a `Prefix` path `/` to the Service `probe` on port 80, and `spec.tls` with the host `probe.local` and the Secret `probe-tls`. Set the annotations `traefik.ingress.kubernetes.io/router.entrypoints: websecure` and `traefik.ingress.kubernetes.io/router.tls: "true"`.
3. Prove the result. A client that trusts the certificate in `probe-tls` must get a response with `version=v1` from `https://probe.local`, and must reject the connection when it asks for a different server name.

## Constraints

- Keep the `probe` Deployment and the Service `probe` unchanged.
- Use the supplied Secret `probe-tls`. Do not create another certificate.

## How the answer is checked

The grader runs two checks. The first reads the Ingress `probe` and needs class `traefik`, the two Traefik annotations, the host `probe.local` with the `Prefix` path `/` to the Service `probe` on port 80, and `spec.tls` with `probe.local` and `probe-tls`. The second runs from inside the `probe` pod. It connects to the Traefik Service on port 443 with the certificate from `probe-tls` as its only trusted certificate. `https://probe.local` must answer with status 200 and `version=v1`, and a handshake for the server name `wrong.local` must be rejected. Both checks also need the `probe` Deployment fully rolled out.

Hint: Traefik picks up a new Ingress a few seconds after you apply it. Repeat your test request before you submit.
