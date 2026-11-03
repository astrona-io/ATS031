---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Disable Profiling And Restrict The API Server Manifest Solution

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-03-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-03-02" || exit 1
NODE=astro-ats-031-lab-020-03-02-control-plane
```

## Add the flag through a copy

Copy the manifest with its mode, insert the flag after the line `- kube-apiserver`, and move the copy into place:

```sh
podman exec $NODE mkdir -p /etc/kubernetes/edit
podman exec $NODE cp -p /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/edit/kube-apiserver.yaml
podman exec $NODE sed -i 's|^\( *\)- kube-apiserver$|&\n\1- --profiling=false|' /etc/kubernetes/edit/kube-apiserver.yaml
podman exec $NODE mv /etc/kubernetes/edit/kube-apiserver.yaml /etc/kubernetes/manifests/kube-apiserver.yaml
```

## Fix the owner and the mode

```sh
podman exec $NODE chown root:root /etc/kubernetes/manifests/kube-apiserver.yaml
podman exec $NODE chmod 600 /etc/kubernetes/manifests/kube-apiserver.yaml
until kubectl --request-timeout=3s get --raw=/readyz >/dev/null 2>&1; do sleep 3; done
```

## Verify The Result

```sh
kubectl -n kube-system get pod kube-apiserver-$NODE -o jsonpath='{.spec.containers[0].command}' | tr ',' '\n' | grep profiling
podman exec $NODE stat -c '%a %U:%G' /etc/kubernetes/manifests/kube-apiserver.yaml
```

The first command prints `--profiling=false`, and the second prints `600 root:root`. If the pod still shows the old arguments, wait for the kubelet to restart the component and run the command again.

After recording your result, remove the independent lab with `astrona destroy ats-031-lab-020-03-02`.

## Common pitfalls

> [!WARNING]
> - **Losing the mode in the copy.** Use `cp -p` and set the mode again at the end.
> - **Checking only the file.** The grader reads the running pod, so wait for the restart.
> - **Leaving a backup in the manifests directory.** Keep it outside.
