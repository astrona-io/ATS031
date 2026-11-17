---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Restore API Server Authorization And Remove Anonymous Access Solution

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-03-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-03-04" || exit 1
node_name="astro-ats-031-lab-020-03-04-control-plane"
worker_name="astro-ats-031-lab-020-03-04-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Reproduce the problem

Start with the request that the test made. `curl -k` skips the check of the server certificate, and without a client certificate or token the API server treats the request as the user `system:anonymous`:

```sh
podman exec "$node_name" curl -sk -o /dev/null -w '%{http_code}\n' https://127.0.0.1:6443/api/v1/namespaces/starfleet-031-020-03-04/pods
```

The API server returns `200`, so the anonymous request can list pods. Two parts decide this: the authentication step accepts the anonymous user, and the authorization step allows the request.

## Restore the authorizers

Read the authorization flag of the running API server:

```sh
podman exec "$node_name" ps -eo args | grep '^kube-apiserver' | tr ' ' '\n' | grep -e '--authorization-mode' -e '--anonymous-auth'
```

The value is `AlwaysAllow`. This authorizer allows every request, so RBAC rules are never checked. The kubelet watches `/etc/kubernetes/manifests` and starts every file in it as a static pod. Edit a copy in a work directory outside that folder, check the copy, and move it back in one step, so that the kubelet never reads a half-written file:

```sh
podman exec "$node_name" mkdir -p /etc/kubernetes/edit
podman exec "$node_name" cp -p /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/edit/kube-apiserver.yaml
podman exec "$node_name" sed -i 's|--authorization-mode=AlwaysAllow|--authorization-mode=Node,RBAC|' /etc/kubernetes/edit/kube-apiserver.yaml
podman exec "$node_name" grep -e '--authorization-mode' /etc/kubernetes/edit/kube-apiserver.yaml
podman exec "$node_name" mv /etc/kubernetes/edit/kube-apiserver.yaml /etc/kubernetes/manifests/kube-apiserver.yaml
```

The API server restarts, so `kubectl` fails for up to a minute. Wait until it answers again:

```sh
kubectl get --raw=/readyz
```

## Remove the anonymous binding

Run the anonymous request again. It may still return `200`, because RBAC is now checked, and an RBAC binding still allows the read. Find every ClusterRoleBinding with the subject `system:anonymous`:

```sh
kubectl get clusterrolebindings -o wide | grep -e NAME -e 'system:anonymous'
```

One binding gives the `view` ClusterRole to `system:anonymous`. Delete it, using the name from the output, and send the request again:

```sh
kubectl delete clusterrolebinding <BINDING_NAME>
podman exec "$node_name" curl -sk -o /dev/null -w '%{http_code}\n' https://127.0.0.1:6443/api/v1/namespaces/starfleet-031-020-03-04/pods
podman exec "$node_name" curl -sk https://127.0.0.1:6443/readyz
```

The pod list now returns `403`, and `/readyz` still prints `ok`. Anonymous authentication stays on, but RBAC allows the anonymous user only the health and version paths.

## Common pitfalls

> [!WARNING]
> Setting `--anonymous-auth=false` on a kubeadm API server also blocks the anonymous `/livez` and `/readyz` probes of the kubelet, so the API server pod is restarted again and again. `--authorization-mode` is a list: a second flag adds to the first. Check RBAC bindings to `system:anonymous` and `system:unauthenticated` after you fix the flag.
