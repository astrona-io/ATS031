---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Guided Practice: Review The Kubelet And CoreDNS

This playground is a private kind cluster with one control plane node and one worker node. The kubelet on the worker node runs with weak settings on purpose: anonymous requests are enabled, the authorization mode is `AlwaysAllow`, the read-only port `10255` is open, and two kubelet files have mode `644`.

Use a host shell with the private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

<!-- astrona:playground:renew -->

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-playground-020-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-playground-020-05" || exit 1
worker_name="astro-ats-031-playground-020-05-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers.

## Inspect

Read the effective kubelet settings through the API server and the file modes on the worker node:

```sh
kubectl get --raw "/api/v1/nodes/$worker_name/proxy/configz" | python3 -m json.tool | grep -e anonymous -e '"mode"' -e readOnlyPort -e rotateCertificates
podman exec "$worker_name" stat -c '%a %n' /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
```

Then read the CoreDNS Deployment and its Corefile:

```sh
kubectl -n kube-system get deployment coredns
kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}'
```

A copy of the original kubelet configuration is in `/opt/training/backup` on the worker node. The kubelet stops if its configuration file has a duplicate key, so always remove a key before you append it again.

## Common pitfalls

> [!WARNING]
> Do not set `protectKernelDefaults` here. A kind node shares the kernel of the host, so the setting can stop the kubelet.
