---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Enable Audit Logging On The API Server Solution

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-03-01
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-03-01`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Read the staged policy

An audit policy tells the API server which requests to record and at which level: `None`, `Metadata`, `Request` or `RequestResponse`. The first rule that matches a request decides its level. Read the staged policy before you use it:

```sh
sudo cat /opt/training/audit-policy.yaml
```

The policy skips the health paths, records Secrets only at the `Metadata` level so that the Secret values never reach the log, and records the rest at `Metadata`.

## Place the policy and edit the manifest

The API server runs in a container, so it can read only the host paths that are mounted into its pod. Create the two host directories and copy the policy:

```sh
sudo mkdir -p /etc/kubernetes/policy /var/log/kubernetes/audit /etc/kubernetes/edit
sudo cp /opt/training/audit-policy.yaml /etc/kubernetes/policy/audit-policy.yaml
sudo cp -p /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/edit/kube-apiserver.yaml
```

Open the copy with an editor:

```sh
sudo vi /etc/kubernetes/edit/kube-apiserver.yaml
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
sudo mv /etc/kubernetes/edit/kube-apiserver.yaml /etc/kubernetes/manifests/kube-apiserver.yaml
```

## Verify that events are written

Wait until the new API server answers. Then make a request that the policy records and look for it in the log:

```sh
for attempt in $(seq 1 60); do
  if sudo ps -eo args | grep '^kube-apiserver ' | grep -q -e '--audit-policy-file' && kubectl --request-timeout=3s get --raw=/readyz >/dev/null 2>&1; then echo "new flag visible and API server ready"; break; fi
  sleep 3
done
```

The old API server process can still answer for a few seconds after the `mv`, so the loop waits until the running API server process has the new flag and the API server is ready. It prints `new flag visible and API server ready`. If it ends without that message, run `sudo crictl ps -a --name kube-apiserver` and read the logs of the exited container.

```sh
kubectl -n starfleet-031-020-03-01 create configmap audit-test
sudo grep -c audit-test /var/log/kubernetes/audit/audit.log
```

The `grep -c` command prints a number above zero. Each line of the log is one JSON event with the user, the verb, the resource and the response code.

## Common pitfalls

> [!WARNING]
> A flag without the matching volume makes the API server fail at start, because the file does not exist in its container. A retention value of `0` means no limit, not a short limit. If the API server does not come back, read the newest container log with `crictl logs` and compare the copy with your backup.
