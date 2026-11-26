# Create One Certificate For Two Host Names — Solution

You solve this lab with one certificate and one Secret. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the hosts and the `tls` entry of the Ingress, and that the Secret is missing:

```sh
kubectl -n starfleet-031-030-03-03 get ingress depot
kubectl -n starfleet-031-030-03-03 get ingress depot -o jsonpath='{.spec.tls}{"\n"}'
kubectl -n starfleet-031-030-03-03 get secret depot-tls
```

The last command prints `Error from server (NotFound)`. Until the Secret exists, Traefik serves its own default certificate for both names.

## Step 2: create the self-signed certificate and the Secret (check `depot-certificate`)

A self-signed certificate is signed with its own private key: its issuer and its subject are the same. `-days 30` makes it valid for 30 days. The Subject Alternative Name (SAN) is the list of host names the certificate is valid for, and one certificate can serve both hosts when its SAN lists both, separated by a comma. Create the key and the certificate in one `openssl` run:

```sh
openssl req -x509 -newkey rsa:2048 -nodes -days 30 \
  -keyout depot.key -out depot.crt \
  -subj "/CN=depot.example.test" -addext "subjectAltName=DNS:depot.example.test,DNS:www.depot.example.test"
```

A Secret of type `kubernetes.io/tls` holds the certificate under `tls.crt` and the matching private key under `tls.key`. Create it from the two files:

```sh
kubectl -n starfleet-031-030-03-03 create secret tls depot-tls --cert=depot.crt --key=depot.key
```

Then check the issuer, the subject and the dates:

```sh
openssl x509 -in depot.crt -noout -subject -issuer -dates
```

The subject and the issuer must be the same, and `notAfter` must be 30 days from now.

## Step 3: confirm both names in the SAN (check `depot-san`)

Clients check the host name only in the SAN, not in the Common Name (CN). Check that both names are there:

```sh
openssl x509 -in depot.crt -noout -text | grep -A1 'Subject Alternative Name'
```

The second line must show `DNS:depot.example.test, DNS:www.depot.example.test`.

## Step 4: test HTTPS for both names (check `depot-https`)

Forward the Traefik HTTPS port to your machine:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443 >/dev/null &
```

Wait a second for the port forward, then send one request for each name that trusts only your certificate:

```sh
curl --cacert depot.crt --resolve depot.example.test:8443:127.0.0.1 https://depot.example.test:8443/
curl --cacert depot.crt --resolve www.depot.example.test:8443:127.0.0.1 https://www.depot.example.test:8443/
```

Both commands must print a line that starts with `app=depot`. Stop the port forward with `kill %1`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> A certificate signed by another CA fails: it must be self-signed, with the issuer equal to the subject.
>
> The validity must be 30 days. A certificate valid for another number of days, for example 365, fails the check.
>
> A SAN with only one of the two names breaks HTTPS for the other name. Putting the second name only in the Common Name (CN) does not help: clients read only the SAN.
>
> `tls.key` must be the private key of `tls.crt`. Do not test with `curl -k`.
