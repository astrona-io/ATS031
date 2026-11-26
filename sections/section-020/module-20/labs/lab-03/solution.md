# Run The Node Checks With A kube-bench Job — Solution

You solve this lab with one kube-bench Job. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

kube-bench is a tool that runs the checks of the CIS (Center for Internet Security) Kubernetes Benchmark on the node where it runs. Check that no audit Job exists yet and see the one node of the cluster:

```sh
kubectl -n starfleet-031-020-02-03 get jobs
kubectl get nodes
```

The first command prints `No resources found in starfleet-031-020-02-03 namespace.` The node is both the control plane and the worker.

## Step 2: write and run the Job (check `node-job-completed`)

kube-bench must run where the processes and files are. The worker node checks read the kubelet, so the audit runs in a pod on the node that runs the kubelet. The `--targets node` option runs only the worker node section of the benchmark.

The `hostPath` volumes mount the node directories that the audit commands read. The node binaries are mounted under `/usr/local/mount-from-host/bin`, where the image looks for `kubectl` and `kubelet` to detect the Kubernetes version. In this lab the one node has no taint, so the Job needs no `nodeSelector` and no toleration. On a cluster with separate worker nodes, the scheduler places a pod without a toleration only on nodes without the control plane taint, so the same Job runs on a worker.

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

Apply it and wait until the Job completes:

```sh
kubectl apply -f job-node-audit.yaml
kubectl -n starfleet-031-020-02-03 wait --for=condition=complete job/node-audit --timeout=180s
```

The `wait` command prints `job.batch/node-audit condition met`.

## Step 3: read the kubelet results (check `kubelet-results-logged`)

The worker checks are in section `4` of the benchmark. Section `4.2` holds the kubelet checks, and each result line starts with `[PASS]`, `[FAIL]` or `[WARN]` and the check number:

```sh
kubectl -n starfleet-031-020-02-03 logs job/node-audit | grep -e '^\[INFO\] 4' -e '^== Summary'
kubectl -n starfleet-031-020-02-03 logs job/node-audit | grep -E '^\[(PASS|FAIL|WARN)\] 4\.2\.'
```

The second command prints the kubelet results. If it prints nothing, the pod could not read the kubelet process.

## Step 4: check where it ran (check `ran-on-worker`)

The Job shares the process namespace of the node (`hostPID: true`), so the program can read the command lines of the node processes, such as the kubelet. Print the node of the pod:

```sh
kubectl -n starfleet-031-020-02-03 get pods -l job-name=node-audit -o wide
```

The `NODE` column shows the name of the lab node, the same name that `kubectl get nodes` printed.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Every check fails until the Job `node-audit` has completed. Use the pinned image `docker.io/aquasec/kube-bench:v0.10.6` and `--targets node`; another image or target fails.
>
> A Job without `hostPID: true` sees only its own container, so the kubelet checks report that no kubelet runs and the log has no `4.2` results.
>
> A Job name can be used only once. Delete the old Job before you apply a changed one.
