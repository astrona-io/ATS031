---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Run Traefik On kind Playground

Use this guide to find your way around the playground. It has no tasks and no grading.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-playground-030-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-playground-030-02" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## What is running

Traefik with the API and access log enabled, the `probe` and `scout` applications on Service port 80, a `shuttle` busybox pod, and a spare `outpost` namespace.

## First commands

```sh
kubectl -n ingress-system get all
kubectl -n starfleet get deployment,service
kubectl get ingressclass
```

Create an Ingress with the class `traefik`, then test it through a port forward:

```sh
kubectl -n ingress-system port-forward service/traefik 8080:80
curl -s -H 'Host: fleet.local' http://127.0.0.1:8080/probe
```

The Traefik API is reachable with `kubectl -n ingress-system port-forward deployment/traefik 9000:8080` and the path `/api/http/routers`.

Destroy the playground when you are done:

```sh
astrona destroy ats-031-playground-030-02
```
