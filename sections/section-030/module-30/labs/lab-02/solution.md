# Fix A Missing TLS Secret For An Ingress — Solution

You solve this lab with one new certificate and one Secret. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check which Secret the Ingress names and where Secrets with that name exist:

```sh
kubectl -n starfleet-031-030-03-02 get ingress beacon -o jsonpath='{.spec.tls}{"\n"}'
kubectl get secret -A --field-selector metadata.name=beacon-tls
kubectl -n outpost-031-030-03-02 get secret beacon-tls -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -text | grep -A1 -E 'Subject:|Subject Alternative Name'
```

An Ingress can only use a Secret in its own namespace, so Traefik cannot read `beacon-tls` from `outpost-031-030-03-02` and serves its own default certificate instead. The certificate there also has no Subject Alternative Name (SAN), the list of host names the certificate is valid for. Clients check the name only in the SAN, so they reject that certificate even if you copied it.

## Step 2: create the Secret in the Ingress namespace (check `beacon-tls-secret`)

Create a new private key and a self-signed certificate. A Secret of type `kubernetes.io/tls` holds the certificate under `tls.crt` and the private key under `tls.key`, and the two must belong together:

```sh
openssl req -x509 -newkey rsa:2048 -nodes -days 30 \
  -keyout beacon-tls.key -out beacon-tls.crt \
  -subj "/CN=beacon.example.test" -addext "subjectAltName=DNS:beacon.example.test"
kubectl -n starfleet-031-030-03-02 create secret tls beacon-tls --cert=beacon-tls.crt --key=beacon-tls.key
```

## Step 3: confirm the name in the SAN (check `beacon-san`)

The `-addext "subjectAltName=DNS:beacon.example.test"` option of the command above put the name in the SAN. Check it:

```sh
openssl x509 -in beacon-tls.crt -noout -text | grep -A1 'Subject Alternative Name'
```

The second line must show `DNS:beacon.example.test` and no other name.

## Step 4: test HTTPS with verification (check `beacon-https`)

Traefik watches Secrets and picks up `beacon-tls` without a restart. Forward the Traefik HTTPS port to your machine:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443 >/dev/null &
```

Wait a second for the port forward, then send a request that trusts only the new certificate:

```sh
curl --cacert beacon-tls.crt --resolve beacon.example.test:8443:127.0.0.1 https://beacon.example.test:8443/
```

The command must print a line that starts with `app=beacon`. Stop the port forward with `kill %1`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Copying the Secret from `outpost-031-030-03-02` fails: the check rejects that certificate because it has no SAN.
>
> Do not change the Ingress to point somewhere else. The Ingress `beacon` must keep `secretName: beacon-tls`.
>
> `tls.key` must be the private key of `tls.crt`, and the SAN must not hold a wildcard or a second name such as `wrong.example.test`.
>
> Do not test with `curl -k`. The check verifies the certificate and the server name.
