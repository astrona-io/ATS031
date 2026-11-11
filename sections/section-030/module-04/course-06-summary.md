---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Summary

Traefik keeps the TLS policy in TLS options, loaded from a dynamic configuration file in a ConfigMap. The `default` option applies to every TLS router. `minVersion: VersionTLS13` removes old protocols, `cipherSuites` limits TLS 1.2 ciphers and `sniStrict` refuses unknown server names. Restart the Deployment to load a changed ConfigMap, and prove the policy with `openssl s_client -tls1_2` and `-tls1_3`.

Mutual TLS adds a client certificate. A `clientAuth` section with `RequireAndVerifyClientCert` and a CA file makes Traefik refuse clients that have no certificate or one from another CA. The option is attached to a route with the annotation `router.tls.options`. Test with `curl --cert --key` and read the exit status of the request without a certificate.

The controller is part of the attack surface. Its ClusterRole can read Secrets in every namespace, an insecure API shows the full routing table without a password, and the Service must publish only the entrypoint ports. `kubectl auth can-i --as` and `kubectl get` with a jsonpath show each item.

Rotation means a new key and certificate, an updated Secret and a check on the wire with `openssl s_client`, comparing serial and end date. `openssl x509 -checkend` turns expiry into an exit status for monitoring. A TLS failure is traced in a fixed order: class, Secret, key pair, host and SAN, and the controller log.

Key facts to remember:

- TLS options are not set on the Ingress; they live in the dynamic configuration.
- A change to the ConfigMap needs a restart of the Deployment to be certain.
- An Ingress with an unserved class, a missing Secret or a wrong host is accepted and does not work.
- The serial and the end date prove which certificate is on the wire.



## Independent live assessment

Prepare with [Verify A Live Certificate Rotation](course-04a-verify-live-certificate-rotation.md). [Rotate The Certificate Served By An Ingress](labs/lab-03/question.md) uses its own kind environment. The active TLS Secret contains the supplied replacement certificate and matching key; A fresh verified TLS connection receives the replacement certificate and the original application response.

<!-- astrona:playground:destroy -->
