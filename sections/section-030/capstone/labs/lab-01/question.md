---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Capstone: Secure Two Hosts With Traefik TLS

The platform team must publish `probe.example.test` and `scout.example.test` over HTTPS. Each host needs its own certificate. Plain HTTP must be redirected, old TLS must be refused, and the broken `scout` Ingress must be repaired.

## Starting state

Traefik runs in `ingress-system` with a ConfigMap `traefik-dynamic` that allows TLS 1.2. The namespace `starfleet` holds the working Services `probe` and `scout`. An Ingress `scout` exists but does not work: it names class `nginx` and sends traffic to the wrong Service. No `probe` Ingress and no TLS Secrets exist.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-capstone-030)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-capstone-030" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Create the Secrets `probe-tls` and `scout-tls` of type `kubernetes.io/tls` in `starfleet`, each from a separate certificate with its own host in the Subject Alternative Name. Create the Ingress `probe` and repair the Ingress `scout`, each with class `traefik`, the `websecure` entrypoint, TLS enabled on the router, its own host, a `Prefix` path `/` and the backend Service of the same name on port 80. Set the default TLS option to `VersionTLS13` with `sniStrict: true`. Redirect plain HTTP on the `web` entrypoint to HTTPS. Each host must serve only its own certificate, and the controller must load the new policy.

## Verify the result

The grader sends requests from inside the cluster. For each host it expects a successful HTTPS response from the right application, a refusal of TLS 1.2, a redirect with a `Location` that starts with `https://` and the same host over HTTP, and a rejection when the certificate of the other host is trusted for the name.
