---
exam_objectives:
- Properly set up Ingress with TLS
---
# Publish A Service By Host Name

Allow about 6 minutes for the tasks.

The depot team wants its application on `depot.local` over plain HTTP for an internal test. Write the Ingress.

## Starting state

The namespace `starfleet-031-030-02-03` holds the Deployment `depot` and the Service `depot` on port 80. Traefik serves the IngressClass `traefik` on the entrypoints `web` (HTTP) and `websecure` (HTTPS). There is no Ingress.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-02-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-02-03" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Create the Ingress `depot` in `starfleet-031-030-02-03` with the class `traefik` and the annotation `traefik.ingress.kubernetes.io/router.entrypoints: web`. It has one rule: the host `depot.local` with a `Prefix` path `/` to the Service `depot` on port 80. Every path of `depot.local` must reach `depot` over HTTP. Requests for other hosts and HTTPS requests must get `404`.

## Verify the result

The grader reads the Ingress. It then sends requests from a pod to the Traefik Service: HTTP for `depot.local/manifest`, HTTP for another host, and HTTPS for `depot.local`.
