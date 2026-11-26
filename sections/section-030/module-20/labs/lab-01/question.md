# Route Two Paths Of One Host With An Ingress

In namespace `starfleet-031-030-02-01`, the Deployments and Services `probe` and `scout` run, both on Service port 80, and the Traefik Ingress controller runs in `ingress-system` with the IngressClass `traefik`. Publish both applications under one host name.

1. Create an Ingress named `fleet` with class `traefik` for host `fleet.local`, with a `Prefix` path `/probe` to Service `probe` port 80 and a `Prefix` path `/scout` to Service `scout` port 80.
2. Requests for `fleet.local/probe` and `fleet.local/scout` must reach their own Service.
3. A request for another host, or for another path on `fleet.local`, must get 404 from Traefik.

Do not change the Deployments or Services `probe` and `scout`, and do not create any other Ingress.
