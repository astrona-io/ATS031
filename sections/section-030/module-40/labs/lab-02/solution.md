# Repair Four Broken TLS Ingresses — Solution

You solve this lab with three patches and one new TLS Secret. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

List the Ingresses, their hosts, classes and Secrets, and the Secrets that exist:

```sh
kubectl -n starfleet-031-030-04-02 get ingress
kubectl -n starfleet-031-030-04-02 get ingress -o custom-columns=NAME:.metadata.name,CLASS:.spec.ingressClassName,HOST:.spec.rules[0].host,TLS-HOST:.spec.tls[0].hosts[0],SECRET:.spec.tls[0].secretName
kubectl -n starfleet-031-030-04-02 get secret
```

Compare each column with the name of the Ingress. A TLS Secret (type `kubernetes.io/tls`) holds a certificate in `tls.crt` and its private key in `tls.key`. Traefik serves a certificate for a host only when the Secret exists, the certificate names the host and the key belongs to the certificate. In any other case it serves its own default certificate, and a client that trusts only the Secret's certificate rejects it.

## Step 2: point alpha at the working Secret (check `alpha-ingress`)

The Ingress `alpha` names the Secret `alpha-tls`, which does not exist. The certificate for `alpha.example.test` is in the Secret `alpha-cert`. Change only the Secret name in the `tls` entry, so the Ingress object stays the same one:

```sh
kubectl -n starfleet-031-030-04-02 patch ingress alpha --type=json -p '[{"op":"replace","path":"/spec/tls/0/secretName","value":"alpha-cert"}]'
```

## Step 3: give bravo a matching key pair (check `bravo-ingress`)

The Secret `bravo-tls` holds a certificate for `bravo.example.test` and a private key from another pair. You can see it by comparing the public key inside the certificate with the public key of the private key:

```sh
kubectl -n starfleet-031-030-04-02 get secret bravo-tls -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -pubkey
kubectl -n starfleet-031-030-04-02 get secret bravo-tls -o jsonpath='{.data.tls\.key}' | base64 -d | openssl pkey -pubout
```

The two public keys differ. Create a new private key and a self-signed certificate for `bravo.example.test`, with the name in the Subject Alternative Name (SAN), the list of host names the certificate is valid for:

```sh
openssl req -x509 -newkey rsa:2048 -nodes -days 30 \
  -keyout bravo-tls.key -out bravo-tls.crt \
  -subj "/CN=bravo.example.test" -addext "subjectAltName=DNS:bravo.example.test" >/dev/null 2>&1
```

Replace the Secret with the new pair. The Ingress `bravo` already names `bravo-tls`, so it stays unchanged:

```sh
kubectl -n starfleet-031-030-04-02 delete secret bravo-tls
kubectl -n starfleet-031-030-04-02 create secret tls bravo-tls --cert=bravo-tls.crt --key=bravo-tls.key
```

## Step 4: fix the charlie host (check `charlie-ingress`)

The rule of `charlie` routes the misspelled host `charlie.example.tset`, while its `tls` entry lists `charlie.example.test`. Traefik matches requests by the host in the rule, so no route serves `charlie.example.test`. Correct the host in the rule:

```sh
kubectl -n starfleet-031-030-04-02 patch ingress charlie --type=json -p '[{"op":"replace","path":"/spec/rules/0/host","value":"charlie.example.test"}]'
```

## Step 5: give delta the right class (check `delta-ingress`)

The Ingress `delta` has the class `nginx`. Traefik reads only Ingresses of the class `traefik`, so it ignores `delta`. Change the class:

```sh
kubectl -n starfleet-031-030-04-02 patch ingress delta --type=json -p '[{"op":"replace","path":"/spec/ingressClassName","value":"traefik"}]'
```

## Step 6: test the four hosts (all checks)

Start a port forward to the Traefik HTTPS port in another terminal:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443
```

For each Ingress, save the certificate of the Secret it names, then send a request that trusts only that certificate:

```sh
for name in alpha bravo charlie delta; do
  secret_name=$(kubectl -n starfleet-031-030-04-02 get ingress "$name" -o jsonpath='{.spec.tls[0].secretName}')
  kubectl -n starfleet-031-030-04-02 get secret "$secret_name" -o jsonpath='{.data.tls\.crt}' | base64 -d > "$name.crt"
  curl --cacert "$name.crt" --resolve "$name.example.test:8443:127.0.0.1" "https://$name.example.test:8443/"
done
```

Each of the four requests must print a line that starts with `app=probe`. Stop the port forward with Ctrl+C.

## Step 7: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not delete an Ingress and create it again, even with the same YAML. The check compares each Ingress with the object the lab started with, and a new object fails.
>
> Each Ingress needs exactly one `tls` entry whose hosts list only its own name, and a rule for that same name. A wildcard certificate or a certificate that also names `wrong.example.test` fails the check.
>
> A Secret whose key does not match its certificate looks fine in `kubectl get secret`. Compare the public keys, or create a new pair, before you trust it.
>
> An Ingress with the class `nginx` is ignored by Traefik. Without the class `traefik`, the host gets no route at all.
