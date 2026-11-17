---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Capstone: Secure Two Hosts With Traefik TLS

Solve this question on: `terminal`

The platform team must publish `probe.example.test` and `scout.example.test` over HTTPS. Traefik runs in `ingress-system` with a ConfigMap `traefik-dynamic` that allows TLS 1.2. The namespace `starfleet` holds the working Services `probe` and `scout`. An Ingress `scout` exists but does not work: it names class `nginx` and sends traffic to the wrong Service. No `probe` Ingress and no TLS Secrets exist. Each host needs its own certificate, plain HTTP must be redirected and old TLS must be refused.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-capstone-030)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-capstone-030" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

Allow about 25 minutes for task work. Cluster startup adds time.

## Tasks

1. Create the Secrets `probe-tls` and `scout-tls` of type `kubernetes.io/tls` in `starfleet`, each from a separate certificate with its own host in the Subject Alternative Name.
2. Create the Ingress `probe` and repair the Ingress `scout`. Each has class `traefik`, the `websecure` entrypoint, TLS enabled on the router, its own host and Secret, a `Prefix` path `/` and the backend Service of the same name on port 80.
3. Set the default TLS option in `traefik-dynamic` to `VersionTLS13` with `sniStrict: true`, and make sure the controller loads the new policy.
4. Redirect plain HTTP on the `web` entrypoint to HTTPS.

## Constraints

- Each host must serve only its own certificate.
- Keep the `probe` and `scout` Deployments and Services unchanged.

## How the answer is checked

The grader runs four checks. Every check also needs the `probe` and `scout` Deployments fully rolled out and their Services in place. The live checks send requests from inside the cluster to the Traefik Service, trusting only the certificate stored in each Secret.

- `tls-secrets` reads `probe-tls` and `scout-tls` and needs the type `kubernetes.io/tls`.
- `ingress-routing` needs both Ingresses with class `traefik`, a `200` response over HTTPS from the right application for each host, and a refused handshake when the other host's certificate is trusted for the name. This check is worth two points.
- `tls13-minimum` needs a `200` response over HTTPS for each host, then a refused handshake when the client allows at most TLS 1.2.
- `http-redirect` needs a `301`, `302`, `307` or `308` response over plain HTTP for each host, with a `Location` that starts with `https://` and the same host.

Hint: Traefik reloads its dynamic configuration from the mounted ConfigMap, which can take a short while. Restart the controller if the new TLS option does not apply.
