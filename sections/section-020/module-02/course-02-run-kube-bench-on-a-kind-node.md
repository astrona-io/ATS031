---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Run kube-bench On A kind Node

On a managed host you can install `kube-bench` as a binary and run it. In a cluster you often run it as a Kubernetes Job, because a Job can be scheduled on a chosen node and leaves its output in the pod log. This part runs the control plane audit as a Job on the kind control plane node, then runs the worker audit, and explains what is different on a kind node.

## A Job that audits the control plane

The Job must do four things. It must share the host process namespace so that the audit can see the API server process. It must run on the control plane node, which carries a taint that blocks ordinary pods, so it needs a node selector and a toleration. It must mount the host directories that the audits read. It must run the program with the `master` target.

<!-- astrona:playground:renew -->

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

The mount of `/usr/bin` at `/usr/local/mount-from-host/bin` gives the program access to the component binaries of the node, which it uses to find the Kubernetes version. All mounts are read only, because the tool only reads. Apply the Job and wait for it to finish:

```sh
kubectl apply -f job-kube-bench-master.yaml
kubectl -n default wait --for=condition=complete job/kube-bench-master --timeout=180s
```

If the Job does not complete, read why with `kubectl -n default describe job kube-bench-master` and `kubectl -n default logs job/kube-bench-master`. A missing image on the node, a taint without a toleration and a failed host mount are the usual causes. When the Job completes, print the first lines of the log:

```sh
kubectl -n default logs job/kube-bench-master | head -n 12
```

The first lines name the benchmark edition that the program loaded and start the first section, so you can see which edition judged your cluster. The rest of the log holds one line per check, then the remediation text, then the summary. Part four reads that report line by line.

## Audit the worker node

The worker node needs the `node` target and a different node. The kubelet and its files are on every node, so the control plane Job does not cover the worker. The control plane taint does not apply to the worker, so the Job needs no toleration, and it selects the worker by its host name.

```sh
kubectl get nodes -o name
```

Use the worker name from this list in the node selector. In this playground it is `astro-ats-031-playground-020-02-worker`.

Save this as `job-kube-bench-node.yaml`:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: kube-bench-node
  namespace: default
spec:
  backoffLimit: 0
  template:
    spec:
      hostPID: true
      restartPolicy: Never
      nodeSelector:
        kubernetes.io/hostname: astro-ats-031-playground-020-02-worker
      containers:
      - name: kube-bench
        image: docker.io/aquasec/kube-bench:v0.10.6
        imagePullPolicy: IfNotPresent
        command: ["kube-bench", "run", "--targets", "node"]
        volumeMounts:
        - {name: var-lib-kubelet, mountPath: /var/lib/kubelet, readOnly: true}
        - {name: etc-systemd, mountPath: /etc/systemd, readOnly: true}
        - {name: etc-kubernetes, mountPath: /etc/kubernetes, readOnly: true}
        - {name: usr-bin, mountPath: /usr/local/mount-from-host/bin, readOnly: true}
      volumes:
      - {name: var-lib-kubelet, hostPath: {path: /var/lib/kubelet}}
      - {name: etc-systemd, hostPath: {path: /etc/systemd}}
      - {name: etc-kubernetes, hostPath: {path: /etc/kubernetes}}
      - {name: usr-bin, hostPath: {path: /usr/bin}}
```

Apply it and read the summary at the end of the log:

```sh
kubectl apply -f job-kube-bench-node.yaml
kubectl -n default wait --for=condition=complete job/kube-bench-node --timeout=180s
kubectl -n default logs job/kube-bench-node | tail -n 8
```

The last lines show how many checks passed, failed, produced a warning or were informational. Compare the totals with the control plane run to see that the two targets cover different checks.

## What is different on kind

A kind node is a container, not a virtual machine. The kubelet runs under systemd inside that container, and the control plane runs as static pods, so the file paths of a kubeadm node are present. Three differences can change results. The node container image is not a standard Linux distribution install, so some audits that read systemd unit files or distribution packages can find different paths than they expect. The users and groups of the node container are those of the image, so the file owner checks may differ from a real host. The container runtime and network plugin files that some file checks inspect (for example for the container network interface) belong to the kind setup, not to a production design.

Do not treat every result from a kind node as a statement about a production cluster. Treat it as a way to practise the tool and the workflow. The same Job file, with the node selector changed, works on a kubeadm cluster.

The Job is the way to run the tool inside a cluster. The next question is how the program chooses what to check, and what to do when its choice is wrong.

## Common pitfalls

> [!WARNING]
> - **Forgetting the toleration on the control plane.** The Job stays `Pending` because the node carries the control plane taint.
> - **Running only one target.** The control plane Job does not audit the worker kubelet. Run both.
> - **Leaving old Jobs in place.** A Job keeps its name. Delete a finished Job before you create one with the same name, or give each run its own name.
> - **Reading kind results as production results.** File owners and system paths in a node container can differ from a real host.
