---
exam_objectives:
- Properly set up Ingress with TLS
---
# Serve Two Hosts With Their Own Certificates

Allow about 8 minutes for the tasks.

The Ingress `fleet` publishes two hosts over HTTPS. Clients of `bridge.local` work, but clients of `dock.local` reject the certificate. Find out why and repair the Ingress.

## Starting state

The namespace `starfleet-031-030-01-04` holds the Deployments and Services `bridge` and `dock` on port 80, and the Secrets `bridge-tls` and `dock-tls`. Each Secret holds a certificate whose SAN names only its own host. The Ingress `fleet` routes `bridge.local` to `bridge` and `dock.local` to `dock` on the `websecure` entrypoint.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-01-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-01-04" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Change only the `tls` section of the Ingress `fleet`. It must have one entry for `bridge.local` with the Secret `bridge-tls` and one entry for `dock.local` with the Secret `dock-tls`. Keep both rules as they are and do not change the Secrets.

## Verify the result

The grader reads the `tls` section. It then connects from a pod twice, with the server names `dock.local` and `bridge.local`. Each connection must receive the certificate from its own Secret and complete a verified HTTPS request.
