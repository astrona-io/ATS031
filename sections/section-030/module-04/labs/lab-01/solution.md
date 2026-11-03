---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Require TLS 1.3 And Strict Server Names Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-04-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-04-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Inspect the current policy

```sh
kubectl -n ingress-system get configmap traefik-dynamic -o jsonpath='{.data.dynamic\.yaml}'
```

## Write the new policy

Save this as `dynamic.yaml`:

```yaml
tls:
  options:
    default:
      minVersion: VersionTLS13
      sniStrict: true
```

## Apply it and load it

```sh
kubectl -n ingress-system create configmap traefik-dynamic --from-file=dynamic.yaml --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ingress-system rollout restart deployment/traefik
kubectl -n ingress-system rollout status deployment/traefik
```

## Verify

Open a port forward in a second terminal and test both versions and the unknown name:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443
openssl s_client -connect 127.0.0.1:8443 -servername probe.example.test -tls1_2 </dev/null 2>&1 | grep -E 'Protocol|handshake failure|alert'
openssl s_client -connect 127.0.0.1:8443 -servername probe.example.test -tls1_3 </dev/null 2>&1 | grep -E 'Protocol|Cipher'
openssl s_client -connect 127.0.0.1:8443 -servername unknown.example.test -tls1_3 </dev/null 2>&1 | grep -E 'alert|handshake failure'
```

The TLS 1.2 and unknown name attempts fail, and the TLS 1.3 attempt completes.
## Common pitfalls

> [!WARNING]
> - **Not restarting Traefik.** The mounted file may not be reloaded; restart the Deployment.
> - **Replacing the key `dynamic.yaml` with another file name.** The file provider reads the folder, but keep the same key.
> - **Indentation errors in the YAML.** Read the Traefik log if the policy does not change.

## Clean up

Destroy the lab cluster when you are done:

```sh
astrona destroy ats-031-lab-030-04-01
```
