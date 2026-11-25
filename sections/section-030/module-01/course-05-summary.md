# Summary

An Ingress holds routing rules and does nothing else. An IngressClass names the controller. The Ingress controller, here Traefik, reads the Ingress objects of its class and routes the requests.

A rule matches a request by host and path. `Exact` matches one path, `Prefix` matches whole path elements, and the longest match wins. The backend names the Service port, not the container port. A request that matches no rule gets a `404` from the controller.

A certificate links a public key to the names in its Subject Alternative Names (SAN) field. The client checks three separate things: the chain to a trusted certificate authority, the name, and the validity dates. A client trusts a self-signed certificate only when it is given that certificate as a trusted authority. A certificate that is trusted but issued for another name is still rejected.

A TLS Secret has the type `kubernetes.io/tls` and the keys `tls.crt` and `tls.key`. It must be in the namespace of the Ingress, and the public key of the certificate must match the private key. Base64 is an encoding, not encryption, so access to the Secret gives access to the key. In the Ingress, `spec.tls` lists the hosts and the `secretName`. The controller ends TLS and sends plain HTTP to the Service, unless encryption to the backend is configured.

The client sends the name it wants in the Server Name Indication (SNI) field. The controller picks the certificate by that name before it reads the HTTP `Host` header. When no certificate matches, or the Secret is missing, the controller serves its own default certificate, and the client reports a verification error. The API server does not check the Secret name, so the error appears in the controller log.

Test with the certificate check turned on, using `curl --cacert` and `openssl s_client -verify_hostname`. Do not use `curl -k` as proof, because it skips the identity check.

Key facts to remember:

- The Ingress object stores rules; the controller routes and terminates TLS.
- The client checks the chain, the name and the dates separately.
- The Secret and the Ingress share a namespace.
- A wrong name and a missing Secret both end in the default certificate.

<!-- astrona:playground:destroy -->
