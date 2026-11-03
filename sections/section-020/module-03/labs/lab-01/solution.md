---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Enable Audit Logging On The API Server Solution

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-03-01" || exit 1
NODE=astro-ats-031-lab-020-03-01-control-plane
```

## Prepare the files

The policy must be inside a directory that the API server container can mount, and the log needs a directory on the node. Edit a copy of the manifest in a work directory so that the kubelet never reads a half written file.

```sh
podman exec $NODE mkdir -p /etc/kubernetes/policy /var/log/kubernetes/audit /etc/kubernetes/edit
podman exec $NODE cp /opt/training/audit-policy.yaml /etc/kubernetes/policy/audit-policy.yaml
podman exec $NODE cp -p /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/edit/kube-apiserver.yaml
```

## Edit the copy

Open the copy with an editor:

```sh
podman exec -it $NODE vi /etc/kubernetes/edit/kube-apiserver.yaml
```

Add these five lines to the `command` list of the container, after the line `- kube-apiserver`, with the same indentation as the other flags:

```yaml
    - --audit-policy-file=/etc/kubernetes/policy/audit-policy.yaml
    - --audit-log-path=/var/log/kubernetes/audit/audit.log
    - --audit-log-maxage=30
    - --audit-log-maxbackup=10
    - --audit-log-maxsize=100
```

Add these two entries to the `volumeMounts` list of the container:

```yaml
    - mountPath: /etc/kubernetes/policy
      name: audit-policy
      readOnly: true
    - mountPath: /var/log/kubernetes/audit
      name: audit-log
```

Add these two entries to the `volumes` list at the end of the pod spec:

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

These blocks are fragments of the manifest. Do not apply them with `kubectl`.

## Install the manifest and wait

```sh
podman exec $NODE mv /etc/kubernetes/edit/kube-apiserver.yaml /etc/kubernetes/manifests/kube-apiserver.yaml
until kubectl --request-timeout=3s get --raw=/readyz >/dev/null 2>&1; do sleep 3; done
```

If the loop does not end, list the containers with `podman exec $NODE crictl ps -a --name kube-apiserver`, read the newest log with `crictl logs`, and restore `/opt/training/backup/kube-apiserver.yaml` through the same copy and move steps.

## Verify The Result

Check the flags of the running pod, make a request, and find it in the log:

```sh
kubectl -n kube-system get pod kube-apiserver-$NODE -o jsonpath='{.spec.containers[0].command}' | tr ',' '\n' | grep audit
kubectl -n starfleet get pods
podman exec $NODE tail -n 20 /var/log/kubernetes/audit/audit.log
```

The first command lists the five audit flags. The log should hold lines in JSON with the field `requestURI` for your request.

After recording your result, remove the independent lab with `astrona destroy ats-031-lab-020-03-01`.

## Common pitfalls

> [!WARNING]
> - **A missing mount.** Without the volume entries the API server cannot read the policy, or it loses the log on restart.
> - **A backup in the manifests directory.** The kubelet reads every file there.
> - **Wrong indentation.** A flag or volume entry with other indentation makes the manifest invalid and the API server does not start.
