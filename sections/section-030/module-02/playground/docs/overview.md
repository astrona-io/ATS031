---
exam_objectives:
- Properly set up Ingress with TLS
---
# Run Traefik On kind Playground

Use this guide to find your way around the playground. It has no tasks and no grading.

Work in a shell on your own computer. `kubectl`, the Kubernetes command-line tool, normally already points at the playground cluster after the playground starts. A kubeconfig is the file that tells `kubectl` which cluster to use and which credentials to send. To be sure that you work on the playground and not on another cluster, select the playground's kubeconfig and check the context:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-playground-030-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-playground-030-02" || exit 1
```

The `test` line stops the shell when the context belongs to another cluster. Keep this shell open while you work through the pages of the module.

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
