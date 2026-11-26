# Repair An Ingress Backend And Read The Traefik Router Name

In namespace `starfleet-031-030-02-05`, the Service `beacon` has one port, named `http`, with the number 80. The Ingress `beacon` routes host `beacon.local` on the `web` entrypoint, but Traefik builds no route for it. Traefik runs with its API on port 8080 of the Service `traefik` in `ingress-system`.

1. Fix the backend of the Ingress `beacon` so it names a port the Service `beacon` has. Keep the host `beacon.local`, the `Prefix` path `/` and the `web` entrypoint.
2. Plain HTTP requests for `beacon.local` must reach the Service `beacon`.
3. Read the HTTP routers from the Traefik API and create the ConfigMap `route-evidence` in `starfleet-031-030-02-05` with the key `router`: the name of the router whose rule matches `beacon.local`, exactly as the API prints it, including the part after `@`.

Do not change the Service or the Deployment `beacon`.
