---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Save The Failing API Server Check Ids Solution

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-02-01" || exit 1
node_name="astro-ats-031-lab-020-02-01-control-plane"
worker_name="astro-ats-031-lab-020-02-01-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Run the audit with JSON output

The text report is made for people. The `--json` option prints the same result as one JSON document, so a script can read it. The Job shares the process namespace of the node (`hostPID: true`), so the program can read the command lines of the node processes. The `hostPath` volumes mount the node directories that the audit commands read. The node binaries are mounted under `/usr/local/mount-from-host/bin`, where the image looks for `kubectl` and `kubelet` to detect the Kubernetes version. Save this as `job-api-server-audit.yaml`:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: api-server-audit
  namespace: starfleet-031-020-02-01
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
        command: ["kube-bench", "run", "--targets", "master", "--json"]
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

Apply it, wait until it completes and save the log in a local file:

```sh
kubectl apply -f job-api-server-audit.yaml
kubectl -n starfleet-031-020-02-01 wait --for=condition=complete job/api-server-audit --timeout=180s
kubectl -n starfleet-031-020-02-01 logs job/api-server-audit > api-server-audit.json
```

## Filter the failing API server checks

Each result in the JSON document is an object with a `test_number` and a `status`. The `jq` filter below walks the whole document, keeps the failing results and prints the numbers that start with `1.2.`:

```sh
jq -r '[.. | objects | select(has("test_number")) | select(.status == "FAIL") | .test_number | select(startswith("1.2."))] | sort | .[]' api-server-audit.json > failing-1-2.txt
cat failing-1-2.txt
```

If `jq` is not installed, save this short Python program as `failing_checks.py`. It does the same walk through the document:

```python
import json
import sys

text = open(sys.argv[1]).read()
report, _ = json.JSONDecoder().raw_decode(text[text.index("{"):])
failing = set()


def collect(node):
    if isinstance(node, dict):
        if node.get("status") == "FAIL" and str(node.get("test_number", "")).startswith("1.2."):
            failing.add(node["test_number"])
        for value in node.values():
            collect(value)
    elif isinstance(node, list):
        for value in node:
            collect(value)


collect(report)
print("\n".join(sorted(failing)))
```

Run it on the saved log:

```sh
python3 failing_checks.py api-server-audit.json > failing-1-2.txt
```

## Record the list

Create the ConfigMap from the file:

```sh
kubectl -n starfleet-031-020-02-01 create configmap failing-checks --from-file=ids=failing-1-2.txt
kubectl -n starfleet-031-020-02-01 get configmap failing-checks -o yaml
```

The key `ids` holds one check number on each line. Do not change any API server setting now, because the grader compares your list with a new run.

## Common pitfalls

> [!WARNING]
> A `grep` on the text report also matches the numbers in the remediation block and can miss checks that wrap. A partial list fails, and so does a list with `WARN` checks. A Job name can be used only once; delete the Job before you run it again with other options.
