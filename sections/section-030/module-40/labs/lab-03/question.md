---
exam_objectives:
- Properly set up Ingress with TLS
---
# Require Client Certificates On One Route

Allow about 12 minutes for the tasks.

The vault route must accept only crew members who present a client certificate from the crew certificate authority (CA). The beacon route stays public. Set up mutual TLS (mTLS) for the vault route only.

## Starting state

The namespace `starfleet-031-030-04-03` holds the Services `vault` and `beacon`, their TLS Secrets and the Ingresses `vault` and `beacon` on the `websecure` entrypoint. The Secret `crew-client` holds a client certificate (`tls.crt`), its key (`tls.key`) and the crew CA certificate (`ca.crt`). Traefik reads `dynamic.yaml` from the ConfigMap `traefik-dynamic` in `ingress-system`. Its pod also mounts the ConfigMap `client-ca` at `/etc/traefik/client-ca`, but that ConfigMap does not exist yet.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-04-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-04-03" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Create the ConfigMap `client-ca` in `ingress-system` with the crew CA certificate under the key `client-ca.crt`. Add a TLS option named `mtls` to `dynamic.yaml` that sets `clientAuthType: RequireAndVerifyClientCert` and reads the CA from `/etc/traefik/client-ca/client-ca.crt`; keep the option `default`. Attach the option only to the Ingress `vault` with the annotation `traefik.ingress.kubernetes.io/router.tls.options: mtls@file`. Restart Traefik so it mounts the new ConfigMap.

## Verify the result

The grader reads the annotations and both ConfigMaps. From a pod it then connects to `vault.example.test` without a client certificate, which must fail, and with the crew client certificate, which must return the `vault` response. A request to `beacon.example.test` without a client certificate must still succeed.
