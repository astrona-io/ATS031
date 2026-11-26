# Sign A Server Certificate With The Lab CA — Solution

You solve this lab with one CA-signed certificate and one Secret. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the `tls` entry of the Ingress and the CA Secret:

```sh
kubectl -n starfleet-031-030-03-04 get ingress relay -o jsonpath='{.spec.tls}{"\n"}'
kubectl -n starfleet-031-030-03-04 get secret lab-ca
kubectl -n starfleet-031-030-03-04 get secret relay-tls
```

The last command prints `Error from server (NotFound)`. A certificate authority (CA) is a key pair whose certificate other certificates are signed with. A client that trusts the CA certificate trusts every certificate the CA signed, so the client does not need the server certificate itself.

## Step 2: sign a certificate with the lab CA (check `relay-certificate`)

Copy the CA certificate and the CA private key out of the Secret `lab-ca`:

```sh
kubectl -n starfleet-031-030-03-04 get secret lab-ca -o jsonpath='{.data.tls\.crt}' | base64 -d > ca.crt
kubectl -n starfleet-031-030-03-04 get secret lab-ca -o jsonpath='{.data.tls\.key}' | base64 -d > ca.key
```

Create a new private key and a certificate signing request (CSR). A CSR holds the public key and the requested name, and the CA turns it into a certificate:

```sh
openssl req -newkey rsa:2048 -nodes -keyout relay.key -out relay.csr \
  -subj "/CN=relay.example.test"
```

`openssl x509 -req` signs the CSR. It does not copy extensions from the CSR, so the Subject Alternative Name (SAN), the list of host names the certificate is valid for, comes from an extension file. Save this as `relay.ext`:

```text
subjectAltName=DNS:relay.example.test
extendedKeyUsage=serverAuth
```

Sign the CSR for 30 days, then store the signed certificate and its key as a TLS Secret:

```sh
openssl x509 -req -in relay.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -days 30 -extfile relay.ext -out relay.crt
kubectl -n starfleet-031-030-03-04 create secret tls relay-tls --cert=relay.crt --key=relay.key
```

Then check the issuer and the dates:

```sh
openssl x509 -in relay.crt -noout -subject -issuer -dates
```

The subject must be `CN=relay.example.test` (the exact spelling depends on your `openssl` version), the issuer must be the subject of the lab CA, and `notAfter` must be 30 days from now.

## Step 3: confirm the name in the SAN (check `relay-san`)

The `subjectAltName` line of `relay.ext` put the name in the SAN. Check it:

```sh
openssl x509 -in relay.crt -noout -text | grep -A1 'Subject Alternative Name'
```

The second line must show `DNS:relay.example.test`.

## Step 4: test HTTPS with only the CA trusted (check `relay-https`)

Forward the Traefik HTTPS port to your machine:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443 >/dev/null &
```

Wait a second for the port forward, then send a request that trusts only the CA certificate:

```sh
curl --cacert ca.crt --resolve relay.example.test:8443:127.0.0.1 https://relay.example.test:8443/
```

The command must print a line that starts with `app=relay`. Stop the port forward with `kill %1`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> A self-signed certificate fails: the issuer must be the lab CA, not the certificate itself. Signing with a new CA, or replacing the Secret `lab-ca`, also fails, because the check compares `lab-ca` with the copy in `lab-ca-original`.
>
> Without `-extfile relay.ext`, the signed certificate has no SAN, and clients reject it for `relay.example.test`.
>
> The certificate must be valid for 30 days, and `tls.key` must be the private key of `tls.crt`.
>
> Do not test with `curl -k`. The check trusts only the lab CA and verifies the server name.
