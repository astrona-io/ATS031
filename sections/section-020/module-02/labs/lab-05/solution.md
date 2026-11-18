---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Record The Totals Of A kube-bench Report Solution

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-02-05
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-02-05`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Run the audit

The Job shares the process namespace of the node (`hostPID: true`), so the program can read the command lines of the node processes. The `hostPath` volumes mount the node directories that the audit commands read. The node binaries are mounted under `/usr/local/mount-from-host/bin`, where the image looks for `kubectl` and `kubelet` to detect the Kubernetes version. Save this as `job-master-audit.yaml`:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: master-audit
  namespace: starfleet-031-020-02-05
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
        command: ["kube-bench", "run", "--targets", "master"]
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

Apply it and wait until it completes:

```sh
kubectl apply -f job-master-audit.yaml
kubectl -n starfleet-031-020-02-05 wait --for=condition=complete job/master-audit --timeout=180s
```

## Read the summary

The text report ends with a summary block. Each line gives a number and a state. Read the end of the log:

```sh
kubectl -n starfleet-031-020-02-05 logs job/master-audit | tail -n 12
```

The block `== Summary master ==` and, when kube-bench prints it, `== Summary total ==` hold lines such as `checks PASS`. With one target, both blocks have the same numbers. Note the four numbers.

## Count the failures by section

The first two parts of a check number name the section. Count the `[FAIL]` lines of each section:

```sh
kubectl -n starfleet-031-020-02-05 logs job/master-audit | grep '^\[FAIL\]' | awk '{print $2}' | cut -d. -f1,2 | sort | uniq -c
```

The output gives one line for each section that has failures. A section that is missing from the output has `0` failures.

## Record the numbers

Create the ConfigMap. Replace each placeholder with the number you read:

```sh
kubectl -n starfleet-031-020-02-05 create configmap master-result --from-literal=pass=<PASS> --from-literal=fail=<FAIL> --from-literal=warn=<WARN> --from-literal=info=<INFO> --from-literal=fail-1.1=<FAIL_1_1> --from-literal=fail-1.2=<FAIL_1_2>
kubectl -n starfleet-031-020-02-05 get configmap master-result -o yaml
```

## Common pitfalls

> [!WARNING]
> The `[FAIL]` lines in the remediation block repeat check numbers; count only the result lines that start with `[FAIL]`. A grep for `1.1` without the trailing dot also matches `1.10` and `1.11` of other sections. Use the numbers of this run; a second run after a change gives other numbers.
