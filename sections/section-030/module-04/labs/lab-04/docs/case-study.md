---
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

Traefik runs as the Deployment `traefik` in `ingress-system` with the argument `--api.insecure=true` and a container port and a Service port 8080 named `dashboard`. Its ClusterRole `traefik` allows `get`, `list` and `watch` on Secrets in every namespace. The namespace `starfleet-031-030-04-04` holds the Service `dock`, the Secret `dock-tls` and the Ingress `dock`, which serves `dock.example.test` over HTTPS.

Remove `--api.insecure=true` and the port 8080 from the Deployment and from the Service `traefik`. Remove `secrets` from the ClusterRole `traefik`. Create the Role `traefik-secrets` and the RoleBinding `traefik-secrets` in `starfleet-031-030-04-04` that let the ServiceAccount `ingress-system/traefik` `get`, `list` and `watch` Secrets there. Add the argument `--providers.kubernetesingress.namespaces=starfleet-031-030-04-04` so Traefik reads Ingress objects and Secrets only in that namespace. `https://dock.example.test` must still serve the certificate from `dock-tls`.
