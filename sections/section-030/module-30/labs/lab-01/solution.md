# Create A TLS Secret And Serve An Ingress Over HTTPS — Solution

You solve this lab with one certificate, one Secret and one Ingress. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the application and that no Secret or Ingress exists for it yet:

```sh
kubectl -n starfleet-031-030-03-01 get deployment,service scout
kubectl -n starfleet-031-030-03-01 get secret,ingress
kubectl get ingressclass traefik
```

The Service `scout` listens on port 80 and sends traffic to the pods on port 8080.

## Step 2: create the certificate and the TLS Secret (check `scout-tls-secret`)

Transport Layer Security (TLS) encrypts the connection and proves the server's name with a certificate. A client checks the name only in the Subject Alternative Name (SAN), the list of host names the certificate is valid for, so the SAN must hold `DNS:scout.example.test`. A self-signed certificate is signed with its own private key, so a client trusts it only when it is given this exact certificate.

Create the private key and the certificate with `openssl`:

```sh
openssl req -x509 -newkey rsa:2048 -nodes -days 30 \
  -keyout scout-tls.key -out scout-tls.crt \
  -subj "/CN=scout.example.test" -addext "subjectAltName=DNS:scout.example.test"
```

A Secret of type `kubernetes.io/tls` holds the certificate under `tls.crt` and its private key under `tls.key`. `kubectl create secret tls` builds it from the two files:

```sh
kubectl -n starfleet-031-030-03-01 create secret tls scout-tls --cert=scout-tls.crt --key=scout-tls.key
```

Then check the SAN of the certificate:

```sh
openssl x509 -in scout-tls.crt -noout -text | grep -A1 'Subject Alternative Name'
```

The second line must show `DNS:scout.example.test` and no other name.

## Step 3: create the Ingress with TLS (check `scout-ingress`)

An Ingress is a Kubernetes object that tells an Ingress controller how to route HTTP requests to Services. `spec.ingressClassName: traefik` hands it to Traefik. The annotation `traefik.ingress.kubernetes.io/router.entrypoints: websecure` binds the route to the HTTPS entrypoint, and `spec.tls` tells Traefik to use the Secret `scout-tls` for `scout.example.test`. Traefik terminates TLS and forwards plain HTTP to the pods.

Save this as `ingress-scout.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: scout
  namespace: starfleet-031-030-03-01
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    traefik.ingress.kubernetes.io/router.tls: 'true'
spec:
  ingressClassName: traefik
  rules:
  - host: scout.example.test
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: scout
            port:
              number: 80
  tls:
  - hosts:
    - scout.example.test
    secretName: scout-tls
```

Apply it:

```sh
kubectl apply -f ingress-scout.yaml
```

## Step 4: test HTTPS with verification (check `scout-https`)

Forward the Traefik HTTPS port to your machine:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443 >/dev/null &
```

Wait a second for the port forward, then send a request that trusts only your certificate. `--resolve` sends it to the forwarded port while `curl` still asks for the name `scout.example.test`:

```sh
curl --cacert scout-tls.crt --resolve scout.example.test:8443:127.0.0.1 https://scout.example.test:8443/
```

The command must print a line that starts with `app=scout`. Stop the port forward with `kill %1`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> A certificate with the name only in the Common Name (CN) and no SAN fails: clients read only the SAN. A wildcard or a second name such as `wrong.example.test` in the SAN also fails.
>
> `tls.key` must be the private key of `tls.crt`. Create the Secret from the key and certificate of the same `openssl` run.
>
> The Ingress needs exactly one `tls` entry, for `scout.example.test` with `secretName: scout-tls`, and the `websecure` entrypoint annotation. With a wrong host or Secret name, Traefik serves its own default certificate.
>
> Do not test with `curl -k`. The check verifies the certificate and the server name.
