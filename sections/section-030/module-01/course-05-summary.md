---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Summary

An Ingress holds routing rules. An IngressClass names the controller, and the Ingress controller, here Traefik, reads the Ingress objects of its class and routes the requests. A rule matches by host and path: `Exact` matches one path, `Prefix` matches whole path elements, and the longest match wins. The backend names the Service port, not the container port. A request that matches no rule gets a `404` from the controller.

A certificate links a public key to names in its Subject Alternative Name field. The client checks three separate things: the chain to a trusted certificate authority, the name, and the validity dates. A self-signed certificate is trusted only when the client is given it as a trusted authority. A certificate that is trusted but issued for another name is still rejected.

A TLS Secret has the type `kubernetes.io/tls` and the keys `tls.crt` and `tls.key`. It must be in the namespace of the Ingress, and the public key of the certificate must match the private key. Base64 is an encoding, so access to the Secret gives access to the key. In the Ingress, `spec.tls` lists the hosts and the `secretName`. The controller ends TLS and sends plain HTTP to the Service unless encryption to the backend is configured.

The client sends the requested name in the Server Name Indication field, and the controller picks the certificate by that name before it reads the HTTP `Host` header. With no matching certificate or a missing Secret the controller serves its own default certificate, and the client reports a verification error. The API server does not check the Secret name, so the controller log is where the error appears. Test with verification on, using `curl --cacert` and `openssl s_client -verify_hostname`, and do not use `curl -k` as proof.

Key facts to remember:

- The Ingress object stores rules; the controller routes and terminates TLS.
- Chain, name and dates are checked separately by the client.
- The Secret and the Ingress share a namespace.
- A wrong name and a missing Secret both end in the default certificate.

<!-- astrona:playground:destroy -->
