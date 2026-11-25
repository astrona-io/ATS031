# Run kube-bench On A kubeadm Node

On a node where you have a shell, you can run `kube-bench` as a binary. That is the usual way in the exam: you log in to a node and run the program as root. In a cluster you can also run it as a Kubernetes Job, which is an object that runs a pod until it finishes. A Job can be scheduled on a chosen node and leaves its output in the pod log. This part runs the binary on the kubeadm node of the playground, then runs the same audit as a Job, and compares the two results.

## Run the binary on the node

The playground node has the binary in `/usr/local/bin/kube-bench`. It reads files that only root can read, such as the static pod manifests in `/etc/kubernetes/manifests`, so run it with `sudo`. A static pod is a pod that the kubelet starts from a manifest file on the node, without the API server; kubeadm runs the API server, the controller manager, the scheduler and etcd this way.

<!-- astrona:playground:renew -->

Open a shell on the node and run the `master` target, which checks the control plane components. Save the report in a file, because the next steps read it more than once:

```sh
astrona ssh astro-ats-031-playground-020-02
sudo kube-bench run --targets master > master.txt
head -n 4 master.txt
tail -n 6 master.txt
```

The first lines start the first section of the benchmark, and the last lines hold the totals:

```text
[INFO] 1 Control Plane Security Configuration
[INFO] 1.1 Control Plane Node Configuration Files
[PASS] 1.1.1 Ensure that the API server pod specification file permissions are set to 600 or more restrictive (Automated)
[PASS] 1.1.2 Ensure that the API server pod specification file ownership is set to root:root (Automated)
== Summary total ==
39 checks PASS
9 checks FAIL
11 checks WARN
0 checks INFO
```

The report does not print the name of the benchmark edition. To see which edition judged the node, add `--v 1`, which turns on log messages, and search for the line that names the edition:

```sh
sudo kube-bench run --targets master --v 1 2>&1 | grep 'Benchmark version'
```

```text
I1118 09:06:28.751611   14047 common.go:351] Kubernetes version: "1.35" to Benchmark version: "cis-1.10"
```

The log line shows that kube-bench detected Kubernetes 1.35 and chose the edition `cis-1.10`. The time stamp and the process number differ on every run.

## Audit the kubelet on the same node

The kubelet is the agent on every node that starts the pods. Its checks are in the `node` target. On a cluster with separate worker nodes you run this target on each worker. In the playground the control plane node also runs the pods, so the `node` target runs on the same machine:

```sh
sudo kube-bench run --targets node | tail -n 6
```

```text
== Summary total ==
16 checks PASS
2 checks FAIL
6 checks WARN
0 checks INFO
```

The `node` target covers other checks than the `master` target. A control plane node runs a kubelet too, so a complete review of it runs both targets.

## Run the audit as a Job

A Job runs the program from the `kube-bench` container image instead of the binary on the node. The Job must do four things. It must share the host process namespace (`hostPID: true`), so that the audit can see the API server process. It must run on the control plane node, so it needs a node selector. It must mount the host directories that the audits read. It must run the program with the `master` target.

On most clusters the control plane node carries the taint `node-role.kubernetes.io/control-plane:NoSchedule`. A taint is a mark on a node that keeps away every pod without a matching toleration. The playground node has no taint, because it also runs your pods. The Job below has the toleration anyway, so the same file works on a cluster where the taint is set.

Save this as `job-kube-bench-master.yaml`:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: kube-bench-master
  namespace: default
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

The mount of `/usr/bin` at `/usr/local/mount-from-host/bin` gives the program access to the `kubectl` and `kubelet` binaries of the node, which it uses to find the Kubernetes version. All mounts are read only, because the tool only reads. Apply it:

```sh
kubectl apply -f job-kube-bench-master.yaml
```

Then wait for the Job to finish and print the totals from the pod log:

```sh
kubectl -n default wait --for=condition=complete job/kube-bench-master --timeout=180s
kubectl -n default logs job/kube-bench-master | tail -n 6
```

```text
job.batch/kube-bench-master condition met
== Summary total ==
38 checks PASS
9 checks FAIL
12 checks WARN
0 checks INFO
```

If the Job does not complete, read why with `kubectl -n default describe job kube-bench-master` and `kubectl -n default logs job/kube-bench-master`. A missing image on the node, a taint without a toleration and a failed host mount are the usual causes.

## Binary or Job: why the totals differ

The Job found the same 9 failures as the binary, but one check moved from `PASS` to `WARN`. Compare check `1.1.10` in the two reports. The pattern `] 1.1.10 ` matches only the result line, not the remediation text of the check:

```sh
grep '\] 1.1.10 ' master.txt
kubectl -n default logs job/kube-bench-master | grep '\] 1.1.10 '
```

```text
[PASS] 1.1.10 Ensure that the Container Network Interface file ownership is set to root:root (Manual)
[WARN] 1.1.10 Ensure that the Container Network Interface file ownership is set to root:root (Manual)
```

The audit of this check reads the files of the container network interface (CNI) plugin, the program that gives each pod its network, under `/var/lib/cni/networks`. The binary on the node can read that directory. The Job does not mount it, so the audit finds no files and the program reports `WARN`. A Job sees only the host directories that it mounts.

The binary on the node is the simplest and most complete way to run the audit when you have a shell on the node. The Job is the way to run it when you only have `kubectl`, and its result depends on the mounts in its file. The next question is how the program chooses what to check, and what to do when its choice is wrong.

## Common pitfalls

> [!WARNING]
> - **Running the binary without `sudo`.** Without root the program cannot read the manifests and data directories, and checks fail for the wrong reason.
> - **Forgetting the toleration on a tainted control plane.** On a cluster where the control plane carries the taint, the Job stays `Pending`.
> - **Running only one target.** The `master` target does not audit the kubelet. Run `node` too, on every node.
> - **Leaving old Jobs in place.** A Job keeps its name. Delete a finished Job before you create one with the same name, or give each run its own name.
> - **Missing host mounts in a Job.** A check that reads a directory the Job does not mount reports `WARN` or `FAIL` for the wrong reason.
