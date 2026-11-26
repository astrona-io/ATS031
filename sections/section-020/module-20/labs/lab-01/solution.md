# Save The Failing API Server Check Ids — Solution

You solve this lab with one kube-bench Job and one ConfigMap built from its JSON output. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

kube-bench is a tool that runs the checks of the CIS (Center for Internet Security) Kubernetes Benchmark against the node it runs on. Check that the namespace has no audit Job and no list yet:

```sh
kubectl -n starfleet-031-020-02-01 get jobs,configmaps
```

The list shows no Job, and no ConfigMap named `failing-checks`.

## Step 2: create the audit Job (check `audit-job-options`)

The text report of kube-bench is made for people. The `--json` option prints the same result as one JSON document, so a script can read it. The `--targets master` option runs only the control plane checks, which include the API server checks in group `1.2`.

The Job shares the process namespace of the node (`hostPID: true`), so the program can read the command lines of the node processes. The `nodeSelector` and the toleration place the pod on the control plane node. The `hostPath` volumes mount the node directories that the audit commands read. The node binaries are mounted under `/usr/local/mount-from-host/bin`, where the image looks for `kubectl` and `kubelet` to detect the Kubernetes version.

Save this as `job-api-server-audit.yaml`:

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

Apply it:

```sh
kubectl apply -f job-api-server-audit.yaml
```

## Step 3: wait for the report (check `json-job-completed`)

Wait until the Job completes, then save its log in a local file:

```sh
kubectl -n starfleet-031-020-02-01 wait --for=condition=complete job/api-server-audit --timeout=180s
kubectl -n starfleet-031-020-02-01 logs job/api-server-audit > api-server-audit.json
```

The `wait` command prints `job.batch/api-server-audit condition met`.

## Step 4: record the failing API server checks (check `failing-checks-match`)

Each result in the JSON document is an object with a `test_number` and a `status`. Save this short Python program as `failing_checks.py`. It walks the whole document, keeps the failing results and prints the numbers that start with `1.2.`:

```python
import json
import sys

text = open(sys.argv[1]).read()
report, _ = json.JSONDecoder().raw_decode(text[text.index("{"):])
failing = set()


def collect(node):
    if isinstance(node, dict):
        if node.get("status") == "FAIL" and str(node.get("test_number", "")).startswith("1.2."):
            failing.add(str(node["test_number"]))
        for value in node.values():
            collect(value)
    elif isinstance(node, list):
        for value in node:
            collect(value)


collect(report)
print("\n".join(sorted(failing)))
```

Run it on the saved log and look at the list:

```sh
python3 failing_checks.py api-server-audit.json > failing-1-2.txt
cat failing-1-2.txt
```

Then create the ConfigMap from the file and check it:

```sh
kubectl -n starfleet-031-020-02-01 create configmap failing-checks --from-file=ids=failing-1-2.txt
kubectl -n starfleet-031-020-02-01 get configmap failing-checks -o yaml
```

The key `ids` holds one check number on each line. Do not change any API server setting now, because the grader compares your list with a new run.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Every check fails when a control plane manifest or `/var/lib/kubelet/config.yaml` changed since the start. Record the findings; do not fix them.
>
> A `grep` on the text report also matches numbers in the remediation text and can miss checks. The list must equal the failing `1.2.` checks: a partial list fails, a list with `WARN` checks fails, and so does any number outside `1.2.`.
>
> A Job name can be used only once. Delete the Job before you run it again with other options.
