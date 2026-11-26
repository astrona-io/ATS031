# Create A TLS Secret For An Ingress — Solution

You solve this lab with `openssl` and one Secret. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check that the Ingress names the Secret and that the Secret is missing:

```sh
kubectl -n starfleet-031-030-01-03 get ingress vault -o jsonpath='{.spec.tls[0].secretName}{"\n"}'
kubectl -n starfleet-031-030-01-03 get secret vault-tls
```

The first command prints `vault-tls`. The second fails with `NotFound`. Without the Secret, Traefik, the Ingress controller, has no certificate for `vault.local` and sends its own default certificate.

## Step 2: create the certificate and the key (check `vault-certificate`)

A self-signed certificate is signed with its own private key, so a client trusts it only when it has the certificate itself. Clients check the host name against the Subject Alternative Name (SAN) and ignore the Common Name (CN), so the SAN must contain `DNS:vault.local`. The option `-days 90` sets the validity, and `-addext` adds the SAN:

```sh
openssl req -x509 -newkey rsa:2048 -nodes -days 90 -keyout vault.key -out vault.crt -subj "/CN=vault.local" -addext "subjectAltName=DNS:vault.local"
```

On macOS the system `openssl` may be LibreSSL, which does not support every option. Use OpenSSL 1.1.1 or newer.

Print the SAN and the end date:

```sh
openssl x509 -in vault.crt -noout -ext subjectAltName -enddate
```

The output shows `DNS:vault.local` and an end date 90 days from now.

## Step 3: store the pair as a TLS Secret (check `vault-secret`)

A Secret of type `kubernetes.io/tls` holds a certificate under the key `tls.crt` and its private key under `tls.key`. Before you store the pair, compare the public key in the certificate with the public key of the private key. The two hashes must be the same:

```sh
openssl x509 -in vault.crt -noout -pubkey | openssl sha256
openssl pkey -in vault.key -pubout | openssl sha256
```

`kubectl create secret tls` checks that the files are PEM data and writes them to the right keys with the right type:

```sh
kubectl -n starfleet-031-030-01-03 create secret tls vault-tls --cert=vault.crt --key=vault.key
kubectl -n starfleet-031-030-01-03 get secret vault-tls -o jsonpath='{.type}{"\n"}'
```

The second command prints `kubernetes.io/tls`.

## Step 4: test HTTPS with the new certificate (check `vault-https`)

Traefik watches Secrets and loads the new one for `vault.local`. Forward the Traefik HTTPS port to your machine:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443 >/dev/null &
```

Wait a second for the port forward, then connect with your certificate as the only trusted certificate:

```sh
curl -s --cacert vault.crt --resolve vault.local:8443:127.0.0.1 https://vault.local:8443/
```

The response starts with `app=vault`. Traefik may need a few seconds to load the new Secret, so repeat the request once if it fails at first. Stop the port forward with `kill %1`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> A certificate without a SAN fails: the check reads only the SAN, as current clients do, and ignores the CN.
>
> Do not create an `Opaque` Secret with `kubectl create secret generic`. The check needs the type `kubernetes.io/tls` and the keys `tls.crt` and `tls.key`.
>
> Do not mix a certificate and a key from two different `openssl` runs. The check rejects a key that does not belong to the certificate.
>
> Use `-days 90`. The check accepts a certificate that is valid for 88 to 91 more days.
