---
exam_objectives:
- Properly set up Ingress with TLS
---
# Harden And Troubleshoot Traefik TLS Playground

Use this guide to find your way around the playground. It has no tasks and no grading.

Work in a shell on your own computer. `kubectl`, the Kubernetes command-line tool, normally already points at the playground cluster after the playground starts. A kubeconfig is the file that tells `kubectl` which cluster to use and which credentials to send. To be sure that you work on the playground and not on another cluster, select the playground's kubeconfig and check the context:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-playground-030-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-playground-030-04" || exit 1
```

The `test` line stops the shell when the context belongs to another cluster. Keep this shell open while you work through the pages of the module.

## What is running

Traefik with the ConfigMap `traefik-dynamic` for TLS options, an optional ConfigMap mount `client-ca`, a working TLS Ingress `probe` with a one-day certificate and four broken Ingresses `case-one` to `case-four`.

## First commands

```sh
kubectl -n starfleet get ingress,secret
kubectl -n ingress-system get configmap traefik-dynamic -o jsonpath='{.data.dynamic\.yaml}'
```

Change the TLS options in the ConfigMap and restart Traefik with `kubectl -n ingress-system rollout restart deployment/traefik`. Diagnose a broken Ingress with `kubectl describe` and `kubectl -n ingress-system logs deployment/traefik`.

Destroy the playground when you are done:

```sh
astrona destroy ats-031-playground-030-04
```
