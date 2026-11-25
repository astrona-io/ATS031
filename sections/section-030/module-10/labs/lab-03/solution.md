---
exam_objectives:
- Properly set up Ingress with TLS
---
# Create A TLS Secret From A Certificate And Key Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-01-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-01-03" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Create the certificate and the key

Create the key and a certificate valid for 90 days. The option `-addext` puts the host name in the SAN, which is the field that clients check:

```sh
openssl req -x509 -newkey rsa:2048 -nodes -days 90 -keyout vault.key -out vault.crt -subj "/CN=vault.local" -addext "subjectAltName=DNS:vault.local"
```

On macOS the system `openssl` may be LibreSSL, which does not support every option. Use OpenSSL 1.1.1 or newer.

## Check the pair before you store it

Print the SAN and the end date, then compare the public key of the certificate with the public key of the private key. The two hashes must be the same:

```sh
openssl x509 -in vault.crt -noout -ext subjectAltName -enddate
openssl x509 -in vault.crt -noout -pubkey | openssl sha256
openssl pkey -in vault.key -pubout | openssl sha256
```

## Create the Secret

`kubectl create secret tls` checks that the files are PEM data and writes them to the keys `tls.crt` and `tls.key`:

```sh
kubectl -n starfleet-031-030-01-03 create secret tls vault-tls --cert=vault.crt --key=vault.key
kubectl -n starfleet-031-030-01-03 get secret vault-tls -o jsonpath='{.type}{"\n"}'
```

The second command prints `kubernetes.io/tls`.

## Verify with a client

Open a port forward in a second terminal, then connect with your certificate as the only trusted certificate:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443
curl -s --cacert vault.crt --resolve vault.local:8443:127.0.0.1 https://vault.local:8443/
```

The response starts with `app=vault`. Traefik may need a few seconds to load the new Secret, so repeat the request once if it fails at first.

## Common pitfalls

> [!WARNING]
> - **A certificate without a SAN.** Current clients ignore the Common Name (CN) and reject the certificate.
> - **Creating an `Opaque` Secret.** A generic Secret has the wrong type and often the wrong key names. Use `kubectl create secret tls`.
> - **Mixing a certificate and a key from two different runs.** Compare the public key hashes before you create the Secret.

## Clean up

Destroy the lab cluster when you are done:

```sh
astrona destroy ats-031-lab-030-01-03
```
