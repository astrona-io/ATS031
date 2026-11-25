---
exam_objectives:
- Properly set up Ingress with TLS
---
# Repair The Traefik Installation

Allow about 10 minutes for the tasks.

A colleague installed Traefik in this cluster, but the Ingress `cargo` gets no route and every request returns `404`. The Ingress itself is correct. Read the installation and repair it.

## Starting state

Traefik runs as the Deployment `traefik` in the namespace `ingress-system`, with the ServiceAccount `traefik` and the ClusterRole `traefik`. The IngressClass `traefik` names the controller `traefik.io/ingress-controller`. The namespace `starfleet-031-030-02-02` holds the Deployment and Service `cargo` and the Ingress `cargo` for `cargo.local` on the `web` entrypoint, with the class `traefik`. The installation has two mistakes.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-02-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-02-02" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Fix the argument of the Deployment `traefik` that selects the IngressClass, so Traefik watches the class `traefik`. Give the ClusterRole `traefik` the missing read access that Traefik needs to find the pod addresses behind a Service. The ClusterRole must keep only the verbs `get`, `list` and `watch`. Change only the other arguments if you must, and do not change the Ingress `cargo`. After the repair, a plain HTTP request with the host `cargo.local` must reach `cargo`.

## Verify the result

The grader reads the Traefik arguments and asks the API server with `kubectl auth can-i` what the ServiceAccount `traefik` may do. It reads the verbs of the ClusterRole and sends an HTTP request for `cargo.local` from a pod to the Traefik Service.
