# Rotate An Expiring Certificate — Solution

You solve this lab with one new key pair and one in-place update of a Secret. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Read the end date of the current certificate and check which Secret the Ingress names:

```sh
kubectl -n starfleet-031-030-04-05 get secret orbit-tls -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -subject -enddate
kubectl -n starfleet-031-030-04-05 get ingress orbit -o jsonpath='{.spec.tls[0].secretName}'; echo
```

The certificate for `orbit.example.test` ends in about two days. The Ingress `orbit` names the Secret `orbit-tls`, so a rotation only has to change the data of that Secret.

## Step 2: create a new certificate (check `orbit-renewed`)

A rotation creates a new private key and a new certificate, not only a new end date. Clients check the host name in the Subject Alternative Name (SAN), the list of host names the certificate is valid for, so the name must be in `subjectAltName`. `-days 90` sets the validity.

```sh
openssl req -x509 -newkey rsa:2048 -nodes -days 90 \
  -keyout orbit.key -out orbit.crt \
  -subj "/CN=orbit.example.test" -addext "subjectAltName=DNS:orbit.example.test" >/dev/null 2>&1
openssl x509 -in orbit.crt -noout -text | grep -A1 'Subject Alternative Name'
openssl x509 -in orbit.crt -noout -enddate
```

The second command shows `DNS:orbit.example.test`, and the third an end date 90 days from now. The check turns green once the next step stores the certificate in the Secret.

## Step 3: replace the Secret data in place (check `orbit-key`)

The command below builds a Secret named `orbit-tls` from the new pair without sending it (`--dry-run=client -o yaml`), and `kubectl apply` writes it over the existing Secret. The Secret object stays the same one, so the Ingress and Traefik keep using it. `-newkey` in the previous step made a new private key, and `--key` stores the key that belongs to `orbit.crt`.

```sh
kubectl -n starfleet-031-030-04-05 create secret tls orbit-tls --cert=orbit.crt --key=orbit.key \
  --dry-run=client -o yaml | kubectl apply -f -
```

## Step 4: test the served certificate (check `orbit-served`)

Traefik watches the Secret through the Kubernetes API and loads the new certificate without a restart. Start a port forward to the Traefik HTTPS port in another terminal:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443
```

Then compare the served certificate with the new one, and send a request that trusts only the new certificate:

```sh
openssl s_client -connect 127.0.0.1:8443 -servername orbit.example.test </dev/null 2>/dev/null | openssl x509 -noout -enddate
openssl x509 -in orbit.crt -noout -enddate
curl --cacert orbit.crt --resolve orbit.example.test:8443:127.0.0.1 https://orbit.example.test:8443/
```

The two end dates must be the same. The `curl` command must print a line that starts with `app=orbit`. If the served end date is still the old one, wait a few seconds and run the first command again. Stop the port forward with Ctrl+C.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not delete the Secret `orbit-tls` and create it again. The check compares it with the object the lab started with, and a new object fails, even with the right data.
>
> Do not reuse the old private key with a new certificate. The check requires a new key that matches the new certificate.
>
> A certificate with the host name only in the Common Name (CN) and no SAN fails: the checks read only the SAN. The validity must be 90 days.
>
> Do not change the ConfigMap `orbit-previous` or point the Ingress at another Secret. The checks use the old copy to prove that the certificate changed, and the Ingress must keep `orbit-tls`.
