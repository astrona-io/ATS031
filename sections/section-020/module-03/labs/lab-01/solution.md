---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Enable Audit Logging On The API Server Solution

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-03-01" || exit 1
node_name="astro-ats-031-lab-020-03-01-control-plane"
worker_name="astro-ats-031-lab-020-03-01-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Read the staged policy

An audit policy tells the API server which requests to record and at which level: `None`, `Metadata`, `Request` or `RequestResponse`. The first rule that matches a request decides its level. Read the staged policy before you use it:

```sh
podman exec "$node_name" cat /opt/training/audit-policy.yaml
```

The policy skips the health paths, records Secrets only at the `Metadata` level so that the Secret values never reach the log, and records the rest at `Metadata`.

## Place the policy and edit the manifest

The API server runs in a container, so it can read only the host paths that are mounted into its pod. Create the two host directories and copy the policy:

```sh
podman exec "$node_name" mkdir -p /etc/kubernetes/policy /var/log/kubernetes/audit /etc/kubernetes/edit
podman exec "$node_name" cp /opt/training/audit-policy.yaml /etc/kubernetes/policy/audit-policy.yaml
podman exec "$node_name" cp -p /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/edit/kube-apiserver.yaml
```

Open the copy with an editor:

```sh
podman exec -it "$node_name" vi /etc/kubernetes/edit/kube-apiserver.yaml
```

Add five flags to the `command` list, after the line `- kube-apiserver`, with the same indentation as the other flags:

```yaml
    - --audit-policy-file=/etc/kubernetes/policy/audit-policy.yaml
    - --audit-log-path=/var/log/kubernetes/audit/audit.log
    - --audit-log-maxage=30
    - --audit-log-maxbackup=10
    - --audit-log-maxsize=100
```

Add two entries under `volumeMounts:` of the container:

```yaml
    - mountPath: /etc/kubernetes/policy
      name: audit-policy
      readOnly: true
    - mountPath: /var/log/kubernetes/audit
      name: audit-log
```

Add two entries under `volumes:` of the pod:

```yaml
  - hostPath:
      path: /etc/kubernetes/policy
      type: DirectoryOrCreate
    name: audit-policy
  - hostPath:
      path: /var/log/kubernetes/audit
      type: DirectoryOrCreate
    name: audit-log
```

`--audit-log-maxage` keeps old log files for 30 days, `--audit-log-maxbackup` keeps at most 10 old files, and `--audit-log-maxsize` starts a new file at 100 megabytes. Save the file, then move it back into the manifests directory:

```sh
podman exec "$node_name" mv /etc/kubernetes/edit/kube-apiserver.yaml /etc/kubernetes/manifests/kube-apiserver.yaml
```

## Verify that events are written

Wait until the new API server answers. Then make a request that the policy records and look for it in the log:

```sh
kubectl get --raw=/readyz
kubectl -n starfleet-031-020-03-01 create configmap audit-test
podman exec "$node_name" grep -c audit-test /var/log/kubernetes/audit/audit.log
```

The `grep -c` command prints a number above zero. Each line of the log is one JSON event with the user, the verb, the resource and the response code.

## Common pitfalls

> [!WARNING]
> A flag without the matching volume makes the API server fail at start, because the file does not exist in its container. A retention value of `0` means no limit, not a short limit. If the API server does not come back, read the newest container log with `crictl logs` and compare the copy with your backup.
