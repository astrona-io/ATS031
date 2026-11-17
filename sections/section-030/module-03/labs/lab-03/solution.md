---
exam_objectives:
- Properly set up Ingress with TLS
---
# Create A Self-Signed Certificate For Two Names Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-03-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-03-03" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Create the certificate

A self-signed certificate is signed with its own key, so its issuer and its subject are the same. List both names in one `subjectAltName` value, separated by a comma:

```sh
openssl req -x509 -newkey rsa:2048 -nodes -days 30 -keyout depot.key -out depot.crt -subj "/CN=depot.example.test" -addext "subjectAltName=DNS:depot.example.test,DNS:www.depot.example.test"
```

## Inspect it

Print the subject, the issuer, the SAN and the dates. The option `-checkend` tests whether the certificate is still valid after the given number of seconds; 2,505,600 seconds are 29 days:

```sh
openssl x509 -in depot.crt -noout -subject -issuer -ext subjectAltName -dates
openssl x509 -in depot.crt -noout -checkend 2505600
```

The subject and the issuer are the same, the SAN lists both names, and the second command prints `Certificate will not expire`.

## Store it and verify

```sh
kubectl -n starfleet-031-030-03-03 create secret tls depot-tls --cert=depot.crt --key=depot.key
```

Open a port forward in a second terminal, then request both names with the certificate as the only trusted certificate:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443
curl -s --cacert depot.crt --resolve depot.example.test:8443:127.0.0.1 https://depot.example.test:8443/
curl -s --cacert depot.crt --resolve www.depot.example.test:8443:127.0.0.1 https://www.depot.example.test:8443/
```

Both responses start with `app=depot`.

## Common pitfalls

> [!WARNING]
> - **Two `-addext` options for the SAN.** Put both names in one `subjectAltName` value, separated by a comma.
> - **Relying on the CN for the second name.** Clients check only the SAN, so each name must be listed there.
> - **Forgetting `-days`.** The default validity of `openssl req -x509` is 30 days in current OpenSSL, but write it explicitly so the result does not depend on the version.

## Clean up

Destroy the lab cluster when you are done:

```sh
astrona destroy ats-031-lab-030-03-03
```
