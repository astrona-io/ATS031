---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Route Two Services From One Host

Solve this question on: `terminal`

The fleet team wants one host, `fleet.local`, to reach two applications: `/probe` must go to the `probe` Service and `/scout` to the `scout` Service. The cluster runs the Traefik Ingress controller in `ingress-system` with the IngressClass `traefik`. The namespace `starfleet-031-030-02-01` holds the Deployments and Services `probe` and `scout`, both on Service port 80. No Ingress exists yet.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-02-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

Allow about 5 minutes for task work. Cluster startup adds time.

## Tasks

1. Check the names and ports of the Services `probe` and `scout` in `starfleet-031-030-02-01`.
2. Create the Ingress `fleet` in `starfleet-031-030-02-01` for class `traefik` and host `fleet.local`. Add a `Prefix` rule for `/probe` to the Service `probe` on port 80, and a `Prefix` rule for `/scout` to the Service `scout` on port 80.
3. Prove the result. With the header `Host: fleet.local`, `/probe` must reach `probe` and `/scout` must reach `scout`. Any other path on that host, and any other host, must get a 404 from the controller.

## Constraints

- Keep the Deployments and Services `probe` and `scout` unchanged.

## How the answer is checked

The grader runs two checks. The first reads the Ingress `fleet` in `starfleet-031-030-02-01` and needs class `traefik`. The second sends plain HTTP requests from inside the `probe` pod to the Traefik Service on port 80. With the host `fleet.local`, `/probe` must answer 200 from `probe` and `/scout` must answer 200 from `scout`. The host `other.local` with `/probe` must answer 404, and `fleet.local` with `/other` must answer 404. Both checks also need both Deployments fully rolled out and both Services in place.

Hint: test from a pod in the cluster with `wget -q -O- --header 'Host: fleet.local' http://traefik.ingress-system.svc/probe`.
