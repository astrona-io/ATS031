---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Repair Four Broken TLS Ingresses

Allow about 12 minutes for the tasks.

Four Ingresses in `starfleet-031-030-04-02` were deployed with a different mistake each: `alpha`, `bravo`, `charlie` and `delta`. Find each cause and repair it so that every host serves a valid certificate.

## Starting state

Traefik runs in `ingress-system`. The Ingresses `alpha` (host `alpha.example.test`), `bravo`, `charlie` and `delta` exist and send traffic to the Service `probe`. None of them works. The Secrets `alpha-cert`, `bravo-tls`, `charlie-tls` and `delta-tls` exist in `starfleet-031-030-04-02`.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-04-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-04-02" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Repair the four Ingresses. Each one must keep its own host name pattern `<name>.example.test` and use class `traefik`. Each must name a Secret in `starfleet-031-030-04-02` whose certificate matches its host and whose key matches its certificate, and the host in `rules` and in `tls` must be the correct name. Preserve the Deployment and the Service, and do not delete an Ingress.

## Verify the result

The grader reads the four Ingresses and Secrets and then connects to each host from inside the cluster with the certificate from its Secret as the trust anchor. It expects the `probe` response for each host and a rejection for a wrong name.
