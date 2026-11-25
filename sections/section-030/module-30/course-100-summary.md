# Summary

A certificate proves the identity of a server. A client accepts it only when three checks pass. The host name must be in the Subject Alternative Name (SAN), the current time must be inside the validity dates, and the client must trust the certificate authority (CA) that signed it. The common name (CN) alone is not enough for current clients.

A self-signed certificate is its own CA, so a client must be given that exact file to trust it. A CA-signed certificate is easier to manage: clients trust one CA file, and that covers every certificate the CA signs.

`openssl req -x509` creates a key and a self-signed certificate in one command. A CA-signed certificate takes four steps. You create the CA, create a server key and a signing request, sign the request with the CA and an extensions file that holds the SAN, and verify the result with `openssl verify`.

Traefik reads a Secret of type `kubernetes.io/tls` with the keys `tls.crt` and `tls.key`, and `kubectl create secret tls` builds it. The API server does not check that the key and the certificate belong together, so you compare their public keys yourself. The Secret must be in the namespace of the Ingress. Base64 is an encoding, not protection.

The `spec.tls` entry of the Ingress names the hosts and the Secret. The annotations `router.entrypoints: websecure` and `router.tls: 'true'` make the Traefik router a TLS router. You test the route with `curl --cacert --resolve` and with `openssl s_client -servername -verify_hostname`. A test with `-k` skips the check and proves nothing.

For a name that matches no certificate, Traefik serves its default certificate, which no client trusts. A redirect on the `web` entrypoint sends HTTP clients to HTTPS. The HSTS header tells browsers to use only HTTPS for the host, for `max-age` seconds.

Key facts to remember:

- A TLS Secret has the type `kubernetes.io/tls` and the keys `tls.crt` and `tls.key`.
- The Secret and the Ingress share a namespace.
- The SAN must contain the host name; the CN alone is not enough.
- Verify with the CA file and the right server name, never with `-k`.

<!-- astrona:playground:destroy -->
