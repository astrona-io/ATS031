# Summary

Traefik keeps its TLS policy in TLS options, which it loads from a dynamic configuration file in a ConfigMap. The `default` option applies to every TLS router. `minVersion: VersionTLS13` removes old protocol versions, `cipherSuites` limits the TLS 1.2 ciphers and `sniStrict` refuses server names that match no certificate. Restart the Deployment to load a changed ConfigMap, and prove the policy with `openssl s_client -tls1_2` and `-tls1_3`.

Mutual TLS adds a client certificate to the handshake. A `clientAuth` section with `RequireAndVerifyClientCert` and a CA file makes Traefik refuse clients that send no certificate, or one signed by another CA. The annotation `router.tls.options` attaches the option to one route. To test it, send a request with `curl --cert --key` and one without, and read the exit status of the request without a certificate.

The controller itself is part of the attack surface. Its ClusterRole can read Secrets in every namespace. An insecure API shows the full routing table without a password. And the Service must publish only the entrypoint ports. `kubectl auth can-i --as` and `kubectl get` with a jsonpath show each of these items.

Rotation means a new key and certificate, an updated Secret and a check on the wire with `openssl s_client` that compares the serial and the end date. `openssl x509 -checkend` turns the expiry date into an exit status for monitoring. You trace a TLS failure in a fixed order: class, Secret, key pair, host and SAN, and then the controller log.

Key facts to remember:

- TLS options are not set on the Ingress; they live in the dynamic configuration.
- A change to the ConfigMap needs a restart of the Deployment to be certain.
- An Ingress with an unserved class, a missing Secret or a wrong host is accepted and does not work.
- The serial and the end date prove which certificate is on the wire.

<!-- astrona:playground:destroy -->
