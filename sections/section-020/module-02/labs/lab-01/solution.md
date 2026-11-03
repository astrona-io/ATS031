---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Save The Failing API Server Check Ids Solution

Use a host shell with the private kubeconfig for this independent kind environment.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-02-01" || exit 1
```

## Run the audit

The Job must share the host process namespace, mount the host directories that the audits read, and run on the control plane node. That node carries a taint, so the Job needs a toleration.

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

Apply it and wait for it to complete:

```sh
kubectl apply -f job-kube-bench-master.yaml
kubectl -n default wait --for=condition=complete job/kube-bench-master --timeout=180s
```

## Build the list

Each failing line of the text report starts with `[FAIL]`, then the check number. Select the lines for section 1.2, keep the number, and save it:

```sh
kubectl -n default logs job/kube-bench-master | grep -E '^\[FAIL\] 1\.2\.' | awk '{print $2}' | sort -V > failing-1-2.txt
cat failing-1-2.txt
```

The file should show one check number on each line, all starting with `1.2.`. If the file is empty, read the first lines of the log to see which edition was loaded and whether the audit ran.

## Save the list in the cluster

Create the ConfigMap from the file. The key must be `ids`:

```sh
kubectl -n starfleet create configmap failing-checks --from-file=ids=failing-1-2.txt
```

## Verify The Result

Read the ConfigMap back and compare it with the file:

```sh
kubectl -n starfleet get configmap failing-checks -o jsonpath='{.data.ids}'
```

Do not change any cluster setting before you submit, because the grader compares your list with a new audit run. The JSON route with `jq` gives the same list.

After recording your result, remove the independent lab with `astrona destroy ats-031-lab-020-02-01`.

## Common pitfalls

> [!WARNING]
> - **Listing `WARN` checks.** Only the state `FAIL` belongs in the list.
> - **Including other sections.** Keep only numbers that start with `1.2.`.
> - **Using another key.** The ConfigMap key must be `ids`.
> - **Fixing a setting first.** A fix changes the failing list, and the grader compares with the current state.
