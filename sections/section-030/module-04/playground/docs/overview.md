---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Harden And Troubleshoot Traefik TLS Playground

Use this guide to find your way around the playground. It has no tasks and no grading.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-playground-030-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-playground-030-04" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

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
