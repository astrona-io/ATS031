---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Summary

A certificate proves the identity of a server. It must contain the host name in the Subject Alternative Name, it must be inside its validity dates, and the client must trust the CA that signed it. A self-signed certificate is its own CA, so a client must be given that file to trust it. A CA-signed certificate lets clients trust one CA file for every certificate the CA signs.

`openssl req -x509` creates a self-signed certificate with a key in one command. A CA-signed certificate takes four steps: create the CA, create a key and a signing request, sign the request with the CA and an extension file that holds the SAN, and verify the result with `openssl verify`.

Traefik reads a Secret of type `kubernetes.io/tls` with the keys `tls.crt` and `tls.key`. `kubectl create secret tls` builds it. The API server does not check that the pair fits together, so compare the public keys. The Secret must be in the namespace of the Ingress, and base64 is not protection.

The `spec.tls` entry names the hosts and the Secret. The annotations `router.entrypoints: websecure` and `router.tls: 'true'` make the router a TLS router. Test with `curl --cacert --resolve` and with `openssl s_client -servername -verify_hostname`; a test with `-k` proves nothing. Unknown names receive the default certificate, which no client trusts. A redirect on the `web` entrypoint sends HTTP clients to HTTPS, and HSTS tells browsers to stay on HTTPS.

Key facts to remember:

- A TLS Secret has the type `kubernetes.io/tls` and the keys `tls.crt` and `tls.key`.
- The Secret and the Ingress share a namespace.
- The SAN must contain the host name; the CN alone is not enough.
- Verify with the CA file and the right server name, never with `-k`.

<!-- astrona:playground:destroy -->
