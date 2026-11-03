---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Rotate And Replace Certificates

Every certificate expires. A certificate that expires on a route makes every client fail at once, and a leaked key needs a replacement before the end date. Rotation means issuing a new certificate and key, updating the Secret and proving that the new certificate is the one on the wire. This part reads the dates and serial of the current certificate, replaces it and checks the result.

## Read the dates and the serial

The playground certificate for `probe.example.test` is valid for one day. The command `openssl x509 -checkend` exits with 0 when the certificate is still valid after the given number of seconds, and with 1 when it will have expired. That makes it usable in a script or a monitor.

<!-- astrona:playground:renew -->

```sh
kubectl -n starfleet get secret probe-tls -o jsonpath='{.data.tls\.crt}' | base64 --decode > old.crt
openssl x509 -in old.crt -noout -serial -enddate
openssl x509 -in old.crt -noout -checkend 604800; echo "valid for another week: exit=$?"
```

The exit status is 1, because a one-day certificate ends within a week. The serial number identifies this particular certificate, so a changed serial shows a new certificate.

## Issue a new certificate and update the Secret

Create the new pair with a longer life. Then replace the Secret. The command `kubectl create secret tls --dry-run=client -o yaml | kubectl apply -f -` updates the existing Secret instead of failing because it exists.

```sh
openssl req -x509 -nodes -newkey rsa:2048 -days 90 -keyout new.key -out new.crt -subj "/CN=probe.example.test" -addext "subjectAltName=DNS:probe.example.test"
kubectl -n starfleet create secret tls probe-tls --cert=new.crt --key=new.key --dry-run=client -o yaml | kubectl apply -f -
```

Traefik watches the Secret through the Kubernetes API, so the controller loads the new certificate without a restart. Allow a few seconds for the update.

## Prove the new certificate is served

Start the port forward in a second terminal and compare the served serial with the old one:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443
openssl s_client -connect 127.0.0.1:8443 -servername probe.example.test </dev/null 2>/dev/null | openssl x509 -noout -serial -enddate
```

The serial differs from the old one, and the end date is about 90 days away. If the old serial is still served, the Secret was not updated or the controller has not yet reloaded; check with `kubectl -n starfleet get secret probe-tls -o jsonpath='{.metadata.resourceVersion}'` and the Traefik log. Remove the old key from disk when you no longer need it, because an old key that leaks still lets an attacker impersonate the host until the certificate expires.

```mermaid
flowchart LR
    N["New key and certificate"] --> S["Secret updated in place"]
    S --> W["Traefik sees the Secret change"]
    W --> C["Clients get the new serial"]
```

The diagram shows the order: new pair first, then the Secret, then the controller picks it up.

## Common pitfalls

> [!WARNING]
> - **Letting the expiry date pass unnoticed.** Run `-checkend` from a schedule and alert before the end date.
> - **Creating a new Secret name without changing the Ingress.** The Ingress still names the old Secret.
> - **Rotating the certificate but not the key.** After a key leak, always generate a new key.
> - **A new SAN list that misses an old host.** Copy every name the old certificate had.
