---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Repair A TLS Ingress With A Missing Secret

The beacon route was created and then abandoned. Clients get a certificate error for `beacon.example.test`. Find the cause and repair it without deleting the Ingress.

## Starting state

The namespace `starfleet` holds the `beacon` Deployment and Service and an Ingress `beacon` that names the Secret `beacon-tls`. A Secret with that name exists only in the namespace `outpost`, and its certificate has a Common Name but no Subject Alternative Name.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-03-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-03-02" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Make `https://beacon.example.test` work. The Ingress `beacon` must keep class `traefik`, the host `beacon.example.test` and `secretName: beacon-tls`. Create a Secret `beacon-tls` of type `kubernetes.io/tls` in `starfleet` from a certificate that has `beacon.example.test` in its Subject Alternative Name. Do not use the certificate in `outpost`. Preserve the Deployment and the Service.

## Verify the result

The grader reads the Secret in `starfleet`, checks its type, and connects from inside the cluster with that certificate as the trust anchor. It expects the `beacon` response for the right name and a rejection for a wrong name.
