---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Audit The Worker Node With A kube-bench Job Solution

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-02-03
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-02-03`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Write the Job

kube-bench must run where the processes and files are. The worker node checks read the kubelet, so the audit runs in a pod on the node that runs the kubelet. The Job shares the process namespace of the node (`hostPID: true`), so the program can read the command lines of the node processes. The `hostPath` volumes mount the node directories that the audit commands read. The node binaries are mounted under `/usr/local/mount-from-host/bin`, where the image looks for `kubectl` and `kubelet` to detect the Kubernetes version. In this lab the one node is both the control plane and the worker, and it has no taint, so the Job needs no `nodeSelector` and no toleration. On a cluster with separate worker nodes, the scheduler places a pod without a toleration only on nodes without the control plane taint, so the same Job runs on a worker.

Save this as `job-node-audit.yaml`:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: node-audit
  namespace: starfleet-031-020-02-03
spec:
  backoffLimit: 0
  template:
    spec:
      hostPID: true
      restartPolicy: Never
      containers:
      - name: kube-bench
        image: docker.io/aquasec/kube-bench:v0.10.6
        imagePullPolicy: IfNotPresent
        command: ["kube-bench", "run", "--targets", "node"]
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
kubectl apply -f job-node-audit.yaml
```

## Check where it ran and what it found

Wait until the Job completes, then print the node of its pod:

```sh
kubectl -n starfleet-031-020-02-03 wait --for=condition=complete job/node-audit --timeout=180s
kubectl -n starfleet-031-020-02-03 get pods -l job-name=node-audit -o wide
```

The `NODE` column shows `astro-ats-031-lab-020-02-03`. Now read the log. The worker checks are in section `4` of the benchmark:

```sh
kubectl -n starfleet-031-020-02-03 logs job/node-audit | grep -e '^\[INFO\] 4' -e '^== Summary'
kubectl -n starfleet-031-020-02-03 logs job/node-audit | grep '^\[FAIL\]'
```

The log lists the sections `4.1` (worker node configuration files) and `4.2` (kubelet), and ends with a summary of the counts.

## Common pitfalls

> [!WARNING]
> A Job without `hostPID: true` sees only its own container, so the kubelet checks report that no kubelet runs. On a cluster with separate worker nodes, a control plane `nodeSelector` copied from a master Job sends the pod to the wrong node. A Job name can be used only once; delete the old Job before you apply a changed one.
