---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Repair A TLS Ingress With A Missing Secret

Solve this question on: `terminal`

The beacon route was created and then abandoned. Clients get a certificate error for `beacon.example.test`. The namespace `starfleet-031-030-03-02` holds the `beacon` Deployment and Service and the Ingress `beacon`, which names the Secret `beacon-tls`. A Secret with that name exists only in the namespace `outpost-031-030-03-02`, and its certificate has a Common Name but no Subject Alternative Name (SAN), the certificate field that lists the names it is valid for.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-03-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-03-02" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

Allow about 6 minutes for task work. Cluster startup adds time.

## Tasks

1. Find out why `https://beacon.example.test` fails. Compare the Secret that the Ingress `beacon` names with the Secrets in both namespaces.
2. Create a certificate and key with `beacon.example.test` in the SAN, and store them as the Secret `beacon-tls` of type `kubernetes.io/tls` in `starfleet-031-030-03-02`.
3. Prove the result. A client that trusts your certificate must get the `beacon` response from `https://beacon.example.test`, and must reject the connection for a wrong server name.

## Constraints

- Do not delete the Ingress `beacon`. It keeps class `traefik`, the host `beacon.example.test` and `secretName: beacon-tls`.
- Do not use the certificate in `outpost-031-030-03-02`.
- Keep the `beacon` Deployment and Service unchanged.

## How the answer is checked

The grader runs two checks. The first needs the Secret `beacon-tls` of type `kubernetes.io/tls` in `starfleet-031-030-03-02`. The second runs from inside the `probe` pod. It connects to the Traefik Service on port 443 with the certificate in that Secret as its only trusted certificate. `https://beacon.example.test` must answer 200 from the Service `beacon`, and a handshake for the server name `wrong.example.test` must be rejected. Both checks also need the Ingress `beacon` with class `traefik` and `spec.tls` for `beacon.example.test` with `beacon-tls`, the `beacon` Deployment fully rolled out and the Service `beacon` in place.
