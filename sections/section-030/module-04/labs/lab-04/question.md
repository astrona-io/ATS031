---
exam_objectives:
- Properly set up Ingress with TLS
---
# Close The Traefik API And Restrict Secret Reads

Allow about 12 minutes for the tasks.

A security review of the cluster found two problems in the Traefik installation: the API answers without authentication on port 8080, and the controller can read every Secret in the cluster. Fix both without breaking the HTTPS route of `dock`.

## Starting state

Traefik runs as the Deployment `traefik` in `ingress-system` with the argument `--api.insecure=true` and a container port and a Service port 8080 named `dashboard`. Its ClusterRole `traefik` allows `get`, `list` and `watch` on Secrets in every namespace. The namespace `starfleet-031-030-04-04` holds the Service `dock`, the Secret `dock-tls` and the Ingress `dock`, which serves `dock.example.test` over HTTPS.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-04-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-04-04" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Remove `--api.insecure=true` and the port 8080 from the Deployment and from the Service `traefik`. Remove `secrets` from the ClusterRole `traefik`. Create the Role `traefik-secrets` and the RoleBinding `traefik-secrets` in `starfleet-031-030-04-04` that let the ServiceAccount `ingress-system/traefik` `get`, `list` and `watch` Secrets there. Add the argument `--providers.kubernetesingress.namespaces=starfleet-031-030-04-04` so Traefik reads Ingress objects and Secrets only in that namespace. `https://dock.example.test` must still serve the certificate from `dock-tls`.

## Verify the result

The grader reads the Traefik arguments and the Service ports, and tries to open port 8080 of the Traefik Service from a pod. It asks the API server with `kubectl auth can-i` which Secrets the ServiceAccount `traefik` may read. It then connects to `dock.example.test` and compares the served certificate with `dock-tls`.
