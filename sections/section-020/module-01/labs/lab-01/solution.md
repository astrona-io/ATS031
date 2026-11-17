---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Correct The Scheduler Bind Address And Record It Solution

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-01-01" || exit 1
node_name="astro-ats-031-lab-020-01-01-control-plane"
worker_name="astro-ats-031-lab-020-01-01-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Confirm the finding

Check 1.4.2 of the benchmark asks that the scheduler binds only to the loopback address `127.0.0.1`. The scheduler serves health and metrics on its secure port `10259`, and nothing outside the node needs to reach it. First, read the flag of the running process:

```sh
podman exec "$node_name" ps -eo args | grep '^kube-scheduler' | tr ' ' '\n' | grep -e '--bind-address'
```

The flag is `--bind-address=0.0.0.0`. Now test the port from the node itself, once on the loopback address and once on the node's own address. The `/healthz` path of the scheduler answers without credentials:

```sh
node_address="$(kubectl get node "$node_name" -o jsonpath='{.status.addresses[?(@.type=="InternalIP")].address}')"
podman exec "$node_name" curl -sk -m 3 https://127.0.0.1:10259/healthz
podman exec "$node_name" curl -sk -m 3 "https://$node_address:10259/healthz"
```

Both requests print `ok`. The second one shows the finding: any client that can reach the node address can reach the scheduler port.

## Change the manifest safely

The kubelet watches `/etc/kubernetes/manifests` and starts every file in it as a static pod. So keep the backup in another directory, edit a copy, and move the copy back in one step:

```sh
podman exec "$node_name" mkdir -p /root/backup /etc/kubernetes/edit
podman exec "$node_name" cp -p /etc/kubernetes/manifests/kube-scheduler.yaml /root/backup/kube-scheduler.yaml
podman exec "$node_name" cp -p /etc/kubernetes/manifests/kube-scheduler.yaml /etc/kubernetes/edit/kube-scheduler.yaml
podman exec "$node_name" sed -i 's|--bind-address=0.0.0.0|--bind-address=127.0.0.1|' /etc/kubernetes/edit/kube-scheduler.yaml
podman exec "$node_name" grep -e '--bind-address' /etc/kubernetes/edit/kube-scheduler.yaml
podman exec "$node_name" mv /etc/kubernetes/edit/kube-scheduler.yaml /etc/kubernetes/manifests/kube-scheduler.yaml
```

The `grep` line shows the new value before the kubelet sees the file. The kubelet then stops the old scheduler and starts a new one. This takes up to a minute.

## Verify the running process

Run the checks from the start again until they show the new state:

```sh
podman exec "$node_name" ps -eo args | grep '^kube-scheduler' | tr ' ' '\n' | grep -e '--bind-address'
podman exec "$node_name" curl -sk -m 3 https://127.0.0.1:10259/healthz
podman exec "$node_name" curl -sk -m 3 "https://$node_address:10259/healthz"
kubectl -n kube-system get pod "kube-scheduler-$node_name"
```

The flag is now `--bind-address=127.0.0.1`. The request to `127.0.0.1` still prints `ok`, and the request to the node address fails because nothing listens there. The pod is `Running` and ready.

## Record the decision

Save this as `configmap-benchmark-review.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: benchmark-review
  namespace: starfleet-031-020-01-01
data:
  component: kube-scheduler
  check: "1.4.2"
  setting: bind-address
  result: corrected
```

Apply it:

```sh
kubectl apply -f configmap-benchmark-review.yaml
```

Then check the result:

```sh
kubectl -n starfleet-031-020-01-01 get configmap benchmark-review -o yaml
```

## Common pitfalls

> [!WARNING]
> A backup inside `/etc/kubernetes/manifests` becomes a second static pod. A changed manifest is not a closed finding until the new process runs with the new flag, so read the process, not only the file. Quote the check number `"1.4.2"` in YAML.
