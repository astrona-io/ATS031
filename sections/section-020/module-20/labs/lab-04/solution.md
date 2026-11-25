---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Run The etcd Checks With A Pinned Benchmark Edition Solution

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-02-04
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-02-04`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Read the requested edition

Without `--benchmark`, kube-bench detects the Kubernetes version and maps it to an edition. The `--benchmark` option names the edition directly. Read the edition that the team asks for:

```sh
kubectl -n starfleet-031-020-02-04 get configmap audit-request -o jsonpath='{.data.benchmark}{"\n"}'
```

## Write the Job

etcd runs on the control plane node, so the Job needs the same `nodeSelector` and toleration as a control plane audit. The Job shares the process namespace of the node (`hostPID: true`), so the program can read the command lines of the node processes. The `hostPath` volumes mount the node directories that the audit commands read. The node binaries are mounted under `/usr/local/mount-from-host/bin`, where the image looks for `kubectl` and `kubelet` to detect the Kubernetes version. The command names the `etcd` target and the edition.

Save this as `job-etcd-audit.yaml`, and replace `<EDITION>` with the value you read:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: etcd-audit
  namespace: starfleet-031-020-02-04
spec:
  backoffLimit: 0
  template:
    spec:
      hostPID: true
      restartPolicy: Never
      nodeSelector:
        node-role.kubernetes.io/control-plane: ""
      tolerations:
      - key: node-role.kubernetes.io/control-plane
        operator: Exists
        effect: NoSchedule
      containers:
      - name: kube-bench
        image: docker.io/aquasec/kube-bench:v0.10.6
        imagePullPolicy: IfNotPresent
        command: ["kube-bench", "run", "--targets", "etcd", "--benchmark", "<EDITION>"]
        volumeMounts:
        - {name: var-lib-etcd, mountPath: /var/lib/etcd, readOnly: true}
        - {name: var-lib-kubelet, mountPath: /var/lib/kubelet, readOnly: true}
        - {name: etc-systemd, mountPath: /etc/systemd, readOnly: true}
        - {name: etc-kubernetes, mountPath: /etc/kubernetes, readOnly: true}
        - {name: usr-bin, mountPath: /usr/local/mount-from-host/bin, readOnly: true}
      volumes:
      - {name: var-lib-etcd, hostPath: {path: /var/lib/etcd}}
      - {name: var-lib-kubelet, hostPath: {path: /var/lib/kubelet}}
      - {name: etc-systemd, hostPath: {path: /etc/systemd}}
      - {name: etc-kubernetes, hostPath: {path: /etc/kubernetes}}
      - {name: usr-bin, hostPath: {path: /usr/bin}}
```

Apply it:

```sh
kubectl apply -f job-etcd-audit.yaml
```

## Check the result

Wait for the Job, then list the section headings and the summary of its log:

```sh
kubectl -n starfleet-031-020-02-04 wait --for=condition=complete job/etcd-audit --timeout=180s
kubectl -n starfleet-031-020-02-04 logs job/etcd-audit | grep -e '^\[INFO\]' -e '^== Summary'
```

The log has only section `2`, the etcd node configuration. If the Job fails instead, read its log: a misspelt edition name makes kube-bench stop with an error.

## Common pitfalls

> [!WARNING]
> A control plane Job with `--targets master` does not run the etcd checks. Without `--benchmark`, kube-bench picks the edition from the detected version, which may not be the edition the team reports against. A misspelt edition name stops the program with an error instead of a result.
