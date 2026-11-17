---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Require TLS 1.3 And Strict Server Names

Solve this question on: `terminal`

Security policy now says that the Ingress controller must refuse TLS 1.2 and must refuse server names it has no certificate for. The Traefik Ingress controller reads its TLS options from the ConfigMap `traefik-dynamic` in `ingress-system`. The default TLS option sets `minVersion: VersionTLS12`. The Ingress `probe` and its Secret `probe-tls` in `starfleet-031-030-04-01` work, and the route `https://probe.example.test` already answers.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-04-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-04-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

Allow about 8 minutes for task work. Cluster startup adds time.

## Tasks

1. Read the default TLS option in the ConfigMap `traefik-dynamic` in `ingress-system`.
2. Change the default TLS option so that `minVersion` is `VersionTLS13` and `sniStrict` is `true`, and make Traefik load the change.
3. Prove the result. `https://probe.example.test` must still answer with the `probe` response over TLS 1.3. A TLS 1.2 handshake must fail, and a handshake for the unknown name `unknown.example.test` must fail.

## Constraints

- Do not change the Ingress `probe`, the Secret `probe-tls` or the application.

## How the answer is checked

The grader runs two checks. Both run from inside the `probe` pod against the Traefik Service on port 443. The first connects with the maximum TLS version set to TLS 1.2 and needs the handshake to be refused. The second connects with the server name `unknown.example.test` and needs the handshake to be refused. Both checks also need `https://probe.example.test` to answer 200 from the Service `probe` with the certificate in `probe-tls` as the trusted certificate, the Ingress `probe` with class `traefik`, the `probe` Deployment fully rolled out and the Service `probe` selecting `app: probe`.
