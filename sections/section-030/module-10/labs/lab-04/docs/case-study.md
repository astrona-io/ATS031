---
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

The namespace `starfleet-031-030-01-04` holds the Deployments and Services `bridge` and `dock` on port 80, and the Secrets `bridge-tls` and `dock-tls`. Each Secret holds a certificate whose SAN names only its own host. The Ingress `fleet` routes `bridge.local` to `bridge` and `dock.local` to `dock` on the `websecure` entrypoint.

Change only the `tls` section of the Ingress `fleet`. It must have one entry for `bridge.local` with the Secret `bridge-tls` and one entry for `dock.local` with the Secret `dock-tls`. Keep both rules as they are and do not change the Secrets.
