---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Create And Verify TLS Playground

Use this guide to find your way around the playground. It has no tasks and no grading.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-playground-030-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-playground-030-03" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## What is running

Traefik with a file provider for TLS options, the `probe` and `scout` applications, a `beacon` application in `outpost`, and no TLS Secrets.

## First commands

```sh
kubectl -n ingress-system get deployment traefik
kubectl get secret --all-namespaces
```

Create a certificate with `openssl`, store it with `kubectl create secret tls`, write an Ingress with `spec.tls`, and test through a port forward:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443
openssl s_client -connect 127.0.0.1:8443 -servername probe.example.test -CAfile ca.crt </dev/null
```

Destroy the playground when you are done:

```sh
astrona destroy ats-031-playground-030-03
```
