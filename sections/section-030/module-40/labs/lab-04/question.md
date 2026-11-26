# Close The Traefik API And Restrict Secret Reads

The Traefik Ingress controller in `ingress-system` runs with its API open on port 8080 and may read Secrets in every namespace. It only needs to serve `https://dock.example.test` from the Ingress `dock` and the Secret `dock-tls` in `starfleet-031-030-04-04`. Reduce what Traefik exposes and what its ServiceAccount `traefik` may read.

1. Remove `secrets` from the ClusterRole `traefik`, and create a Role and a RoleBinding, both named `traefik-secrets`, in `starfleet-031-030-04-04` that let the ServiceAccount `ingress-system/traefik` `get`, `list` and `watch` Secrets there.
2. Remove `--api.insecure=true` and the port 8080 from the Deployment `traefik` and from the Service `traefik`, so port 8080 accepts no connections.
3. Add the argument `--providers.kubernetesingress.namespaces=starfleet-031-030-04-04` to Traefik, and keep `https://dock.example.test` serving the `dock-tls` certificate.

Do not change the Ingress `dock`, the Secret `dock-tls` or the applications.
