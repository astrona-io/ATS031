# Give Each Ingress Host Its Own TLS Certificate

In namespace `starfleet-031-030-01-04`, the Ingress `fleet` publishes `bridge.local` and `dock.local` over HTTPS. Clients of `bridge.local` work, but clients of `dock.local` reject the certificate. The Secrets `bridge-tls` and `dock-tls` each hold a certificate for their own host. Repair the `tls` section of the Ingress.

1. Give `bridge.local` its own `spec.tls` entry with the Secret `bridge-tls`.
2. Give `dock.local` its own `spec.tls` entry with the Secret `dock-tls`, with no other `tls` entries and both rules unchanged.
3. For each server name, Traefik must send the certificate from that host's Secret, and a client that trusts it must get `200` from the Service of the same name.

Change only the `tls` section of the Ingress `fleet`; do not change, delete or create again the Secrets.
