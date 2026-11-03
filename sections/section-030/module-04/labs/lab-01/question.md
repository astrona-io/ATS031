---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Require TLS 1.3 And Strict Server Names

Security policy now says that the Ingress controller must refuse TLS 1.2 and must refuse server names it has no certificate for. The route `probe.example.test` already works.

## Starting state

Traefik reads its TLS options from the ConfigMap `traefik-dynamic` in `ingress-system`. The default option sets `minVersion: VersionTLS12`. The Ingress `probe` and its Secret `probe-tls` in `starfleet` work.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-04-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-04-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Change the default TLS option so that the minimum version is `VersionTLS13` and `sniStrict` is `true`. Make Traefik load the change. The route `https://probe.example.test` must still answer with the `probe` response over TLS 1.3. A TLS 1.2 handshake must fail and a handshake for the unknown name `unknown.example.test` must fail. Do not change the Ingress, the Secret or the application.

## Verify the result

The grader sends requests from inside the cluster with the certificate from `probe-tls` as the trust anchor. It expects a success over TLS 1.3, a refusal with the maximum version set to TLS 1.2 and a refusal for the unknown server name.
