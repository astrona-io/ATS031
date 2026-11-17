---
exam_objectives:
- Properly set up Ingress with TLS
---
# Fix An Ingress That Traefik Ignores

Allow about 6 minutes for the tasks.

The relay team created an Ingress for `relay.local`, but every request to Traefik returns `404 Not Found`. Find the two mistakes in the Ingress and fix them.

## Starting state

The namespace `starfleet-031-030-01-02` holds the Deployment `relay` and the Service `relay`. The Service listens on port 80 and sends traffic to the container port 8080. Traefik serves the IngressClass `traefik` on the entrypoints `web` and `websecure`. The Ingress `relay` exists, but Traefik does not route it.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-01-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-01-02" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Keep the Ingress name `relay`, the host `relay.local`, the `Prefix` path `/` and the `web` entrypoint. The Ingress must name the class `traefik` and send requests to the Service `relay` on its Service port 80. A plain HTTP request with the host `relay.local` must reach `relay`. A request for any other host must still get `404`. Do not change the Deployment or the Service.

## Verify the result

The grader reads the Ingress. It then sends HTTP requests from a pod in the cluster to the Traefik Service, once with the host `relay.local` and once with another host.
