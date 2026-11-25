---
exam_objectives:
- Properly set up Ingress with TLS
---
# Sign A Server Certificate With A Lab CA Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-03-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-03-04" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Extract the CA

Write the CA certificate and key to files. `base64 -d` decodes the Secret data; on older macOS use `base64 -D`:

```sh
kubectl -n starfleet-031-030-03-04 get secret lab-ca -o jsonpath='{.data.tls\.crt}' | base64 -d > ca.crt
kubectl -n starfleet-031-030-03-04 get secret lab-ca -o jsonpath='{.data.tls\.key}' | base64 -d > ca.key
openssl x509 -in ca.crt -noout -subject
```

## Create the key and the request

```sh
openssl req -newkey rsa:2048 -nodes -keyout relay.key -out relay.csr -subj "/CN=relay.example.test"
```

## Sign the request

`openssl x509 -req` does not copy extensions from the request, so the SAN comes from an extension file. Save this as `relay.ext`:

```
subjectAltName=DNS:relay.example.test
extendedKeyUsage=serverAuth
```

Sign the request with the CA and check the result against the CA:

```sh
openssl x509 -req -in relay.csr -CA ca.crt -CAkey ca.key -CAcreateserial -days 30 -extfile relay.ext -out relay.crt
openssl verify -CAfile ca.crt relay.crt
openssl x509 -in relay.crt -noout -issuer -ext subjectAltName
```

`openssl verify` prints `relay.crt: OK`, and the issuer is the CA subject.

## Store and verify

```sh
kubectl -n starfleet-031-030-03-04 create secret tls relay-tls --cert=relay.crt --key=relay.key
```

Open a port forward in a second terminal, then connect with the CA as the only trusted certificate:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443
curl -s --cacert ca.crt --resolve relay.example.test:8443:127.0.0.1 https://relay.example.test:8443/
```

The response starts with `app=relay`. Delete `ca.key` from your machine when you are done.

## Common pitfalls

> [!WARNING]
> - **Expecting the SAN to come from the CSR.** `openssl x509 -req` drops request extensions unless you give `-extfile`.
> - **Storing the CA key in the server Secret.** Traefik needs only the server certificate and the server key.
> - **Signing a self-signed certificate instead of a CSR.** The issuer must be the CA, or clients that trust only the CA reject it.

## Clean up

Destroy the lab cluster when you are done:

```sh
astrona destroy ats-031-lab-030-03-04
```
