---
exam_objectives:
- Properly set up Ingress with TLS
---
# Match Exact And Prefix Paths

Allow about 8 minutes for the tasks.

The API gateway team needs two routes on `api.local`: a health check that must match one path only, and a versioned API that owns everything under `/v1`.

## Starting state

The namespace `starfleet-031-030-02-04` holds the Deployments and Services `beacon` and `scout`, each on port 80. Traefik serves the IngressClass `traefik` on the entrypoints `web` and `websecure`. There is no Ingress.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-02-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-02-04" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Create the Ingress `api` in `starfleet-031-030-02-04` with the class `traefik` on the `web` entrypoint, for the host `api.local`. The path `/healthz` with `pathType: Exact` goes to the Service `beacon` on port 80. The path `/v1` with `pathType: Prefix` goes to the Service `scout` on port 80. Add no other paths, so `/healthz/deep`, `/v2` and `/` get `404`.

## Verify the result

The grader reads the paths of the Ingress. It then sends HTTP requests for `api.local` from a pod to the Traefik Service: `/healthz`, `/healthz/deep`, `/v1`, `/v1/ships/7`, `/v2` and `/`.
