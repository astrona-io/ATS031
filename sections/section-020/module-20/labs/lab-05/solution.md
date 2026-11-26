# Record The Totals Of A kube-bench Report — Solution

You solve this lab with one kube-bench Job and one ConfigMap of numbers read from its log. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

kube-bench is a tool that runs the checks of the CIS (Center for Internet Security) Kubernetes Benchmark on the node where it runs. Check that no audit Job exists yet:

```sh
kubectl -n starfleet-031-020-02-05 get jobs
```

The command prints `No resources found in starfleet-031-020-02-05 namespace.`

## Step 2: run the audit (check `master-job-completed`)

The `--targets master` option runs the control plane checks. The `nodeSelector` and the toleration place the pod on the control plane node. The Job shares the process namespace of the node (`hostPID: true`), so the program can read the command lines of the node processes. The `hostPath` volumes mount the node directories that the audit commands read. The node binaries are mounted under `/usr/local/mount-from-host/bin`, where the image looks for `kubectl` and `kubelet` to detect the Kubernetes version.

Save this as `job-master-audit.yaml`:

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

The `wait` command prints `job.batch/master-audit condition met`.

## Step 3: read the summary totals (check `totals-match`)

The text report ends with a summary block. Each line gives a number and a state, such as `checks PASS`. Print the summary lines:

```sh
kubectl -n starfleet-031-020-02-05 logs job/master-audit | grep -E '^[0-9]+ checks (PASS|FAIL|WARN|INFO)$'
```

The block `== Summary master ==` and, when kube-bench prints it, `== Summary total ==` hold these lines. With one target, both blocks have the same numbers. Note the four numbers.

## Step 4: count the failures by section (check `section-counts-match`)

The first two parts of a check number name the section. Count the `[FAIL]` result lines of each section:

```sh
kubectl -n starfleet-031-020-02-05 logs job/master-audit | grep '^\[FAIL\]' | awk '{print $2}' | cut -d. -f1,2 | sort | uniq -c
```

The output gives one line for each section that has failures. A section that is missing from the output has `0` failures.

Now create the ConfigMap with all six numbers. Replace each placeholder with the number you read:

```sh
kubectl -n starfleet-031-020-02-05 create configmap master-result --from-literal=pass=<PASS> --from-literal=fail=<FAIL> --from-literal=warn=<WARN> --from-literal=info=<INFO> --from-literal=fail-1.1=<FAIL_1_1> --from-literal=fail-1.2=<FAIL_1_2>
```

Then check the result:

```sh
kubectl -n starfleet-031-020-02-05 get configmap master-result -o yaml
```

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Every check fails until the Job `master-audit` has completed with `--targets master`.
>
> The remediation block repeats check numbers. Count only the result lines that start with `[FAIL]`. A grep for `1.1` without the trailing dot also matches `1.10` and `1.11` of other sections.
>
> Use the numbers of this run. Write `0` for a section without failures; an empty value does not match.
