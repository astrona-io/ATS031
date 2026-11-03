---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Route Two Services From One Host

The fleet team wants one host, `fleet.local`, to reach two applications: `/probe` must go to the `probe` Service and `/scout` to the `scout` Service. Create the Ingress that does this on the Traefik controller.

## Starting state

The cluster runs Traefik in `ingress-system` with the IngressClass `traefik`. The namespace `starfleet` holds the Deployments and Services `probe` and `scout`, both on Service port 80. No Ingress exists yet.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-02-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Create an Ingress `fleet` in the namespace `starfleet` for class `traefik` and host `fleet.local`. Add a `Prefix` rule for `/probe` that sends requests to the Service `probe` on port 80, and a `Prefix` rule for `/scout` that sends requests to the Service `scout` on port 80. A request for any other path on that host must receive a 404 from the controller. Preserve the original Deployments and Services.

## Verify the result

The grader checks the Ingress fields and then sends requests with the `Host: fleet.local` header from a pod inside the cluster. It expects the `probe` response on `/probe`, the `scout` response on `/scout` and a 404 for another path. Wait for the controller to pick up the route before you test.
