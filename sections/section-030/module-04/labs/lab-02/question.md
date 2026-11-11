---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Repair Four Broken TLS Ingresses

Solve this question on: `terminal`

Four Ingresses in `starfleet-031-030-04-02` were deployed with a different mistake each: `alpha` (host `alpha.example.test`), `bravo`, `charlie` and `delta`. They send traffic to the Service `probe`, and none of them works. The Secrets `alpha-cert`, `bravo-tls`, `charlie-tls` and `delta-tls` exist in `starfleet-031-030-04-02`. The Traefik Ingress controller runs in `ingress-system`.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-04-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-04-02" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

Allow about 12 minutes for task work. Cluster startup adds time.

## Tasks

1. For each Ingress, compare its host in `rules` and in `tls`, the Secret it names, and the names in that Secret's certificate.
2. Repair `alpha` and `bravo`. Each must name a Secret in `starfleet-031-030-04-02` whose certificate matches its host and whose key matches its certificate, and the host in `rules` and in `tls` must be the correct name.
3. Repair `charlie` and `delta` the same way.
4. Prove the result. A client that trusts each Secret's certificate must get the `probe` response from each `https://<name>.example.test`, and must reject the connection for a wrong server name.

## Constraints

- Each Ingress keeps its own host name pattern `<name>.example.test` and class `traefik`.
- Do not delete an Ingress. Keep the Deployment and the Service unchanged.

## How the answer is checked

The grader runs four checks, one for each Ingress: `alpha`, `bravo`, `charlie` and `delta`. Each check reads the Secret named in the first `spec.tls` entry of that Ingress, then connects from inside the `probe` pod to the Traefik Service on port 443 with that certificate as its only trusted certificate. `https://<name>.example.test` must answer 200 from the Service `probe`, and a handshake for the server name `wrong.example.test` must be rejected. Every check also needs the four Ingresses with class `traefik`, the `probe` Deployment fully rolled out and the Service `probe` selecting `app: probe`.
