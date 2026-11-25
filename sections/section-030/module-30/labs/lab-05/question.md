---
exam_objectives:
- Properly set up Ingress with TLS
---
# Redirect HTTP To HTTPS And Add HSTS

Allow about 10 minutes for the tasks.

The harbor site is published over HTTPS, but users who type `http://` get `404`, and browsers do not remember to use HTTPS. Redirect plain HTTP to HTTPS and add an HTTP Strict Transport Security (HSTS) header.

## Starting state

The namespace `starfleet-031-030-03-05` holds the Deployment `harbor`, the Service `harbor` on port 80, the Secret `harbor-tls` and the Ingress `harbor`. The Ingress routes `harbor.example.test` on the `websecure` entrypoint with TLS. Traefik reads extra dynamic configuration from the ConfigMap `traefik-dynamic` in `ingress-system`, key `dynamic.yaml`, which holds the TLS option `default`.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-03-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-03-05" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Add the two arguments to the Deployment `traefik` that redirect every request on the entrypoint `web` to the entrypoint `websecure` with the scheme `https`. Keep all existing arguments. Add a headers middleware named `hsts` with `stsSeconds: 300` to `dynamic.yaml` in `traefik-dynamic`, and keep the TLS option `default`. Attach the middleware to the Ingress `harbor` with the annotation `traefik.ingress.kubernetes.io/router.middlewares: hsts@file`.

## Verify the result

The grader reads the Traefik arguments and the Ingress annotation. From a pod it sends a plain HTTP request for `harbor.example.test/cargo` and expects a permanent redirect to the same path over HTTPS. It then sends a verified HTTPS request and reads the `Strict-Transport-Security` header.
