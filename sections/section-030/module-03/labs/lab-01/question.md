---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Publish Scout Over HTTPS With Your Own Certificate

Allow about 8 minutes for the tasks.

The scout team needs its application on `scout.example.test` over HTTPS. No certificate exists yet, so you create one, store it in a Secret and write the Ingress.

## Starting state

The cluster runs Traefik with the entrypoints `web` and `websecure`. The namespace `starfleet-031-030-03-01` holds a working `scout` Deployment and Service on port 80. There is no Secret and no Ingress for `scout`.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-03-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Create a self-signed certificate for `scout.example.test` with that name in the Subject Alternative Name. Store it as the Secret `scout-tls` of type `kubernetes.io/tls` in `starfleet-031-030-03-01`. Create an Ingress `scout` for class `traefik` with the host `scout.example.test`, a `Prefix` path `/` to the Service `scout` on port 80, the `websecure` entrypoint, TLS enabled on the router and `scout-tls` in `spec.tls`. A client that trusts your certificate must get the `scout` response for the matching name. Preserve the original Deployment and Service.

## Verify the result

The grader reads the Secret and the Ingress, then connects from inside the cluster with the certificate in your Secret as the only trust anchor. It expects a successful HTTPS response from `scout` for the right name and a rejected connection for a wrong server name.
