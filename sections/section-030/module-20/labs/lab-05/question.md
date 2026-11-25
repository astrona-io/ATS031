---
exam_objectives:
- Properly set up Ingress with TLS
---
# Find A Broken Route With The Traefik API

Allow about 10 minutes for the tasks.

The beacon team reports that `beacon.local` returns `404`, although the Ingress exists. Use the evidence of the controller to find the cause, fix it, and record which router Traefik builds.

## Starting state

The namespace `starfleet-031-030-02-05` holds the Deployment `beacon` and the Service `beacon`. The Service has one port, named `http`, with the number 80. The Ingress `beacon` routes the host `beacon.local` on the `web` entrypoint, but Traefik builds no route for it. In this lab Traefik runs with its API enabled on port 8080 of the Service `traefik` in `ingress-system`.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-02-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-02-05" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Fix the Ingress `beacon` so plain HTTP requests for `beacon.local` reach the Service `beacon`. Keep the host, the path and the entrypoint. Then read the list of HTTP routers from the Traefik API and create the ConfigMap `route-evidence` in `starfleet-031-030-02-05` with the key `router`. Its value is the name of the router whose rule matches `beacon.local`, exactly as the API prints it, including the part after `@`.

## Verify the result

The grader sends an HTTP request for `beacon.local` from a pod to the Traefik Service. It then reads the router list from the Traefik API and compares the router name for `beacon.local` with the value in your ConfigMap.
