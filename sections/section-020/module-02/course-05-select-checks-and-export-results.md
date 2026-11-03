---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Select Checks And Export Results

A full run takes time and prints far more than you need while you fix one setting. During a fix you want to run a single check again and see only its result. At the end of a review you want a file that a script or a colleague can read. This part shows how to select checks, how to export JSON, and how to keep a baseline for a before and after comparison.

## Select checks

The `--check` option takes a comma-separated list of check numbers and runs only those. The `--group` option takes a group number, which is a block of related checks such as all of `1.2`. You add the option to the `command` line of the Job, after `run`. For example, `["kube-bench", "run", "--targets", "master", "--check", "1.2.1,1.2.2"]` runs two checks. Because numbers differ between editions, first find the numbers in a full log, then use them in the same edition.

A rerun of one check has a clear job in the remediation loop: change the setting, wait for the component to restart, run only that check, and see it pass. This is faster than a full run, and it avoids reading hundreds of lines. At the end, one full run proves that the fix did not change other results.

## Export JSON

The text report is made for people. The `--json` option prints the same result as one JSON document, so a script can read it. Run the control plane audit again with this option and save the output. A Job name can be used only once, so this Job has its own name.

<!-- astrona:playground:renew -->

Save this as `job-kube-bench-json.yaml`:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: kube-bench-json
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

Apply it and save the log as the baseline file:

```sh
kubectl apply -f job-kube-bench-json.yaml
kubectl -n default wait --for=condition=complete job/kube-bench-json --timeout=180s
kubectl -n default logs job/kube-bench-json > baseline-master.json
```

If the file holds log lines before the first `{`, remove them with a text editor, because `jq` reads only JSON. Do not assume the layout of the document. Look at its top-level keys first:

```sh
jq 'keys' baseline-master.json
```

The report holds a list of controls, each with tests and results, and a block of totals. In the versions this lesson was written for, a result is an object with fields such as `test_number`, `test_desc` and `status`. Check these names in your file before you rely on them.

## Filter with jq

The filter below walks the whole document and picks every object that has a `test_number` and the status `FAIL`. It prints only the numbers, so it does not depend on how the controls are nested.

```sh
jq -r '[.. | objects | select(has("test_number")) | select(.status == "FAIL") | .test_number] | sort | .[]' baseline-master.json
```

To keep only the API server checks, filter the numbers that start with `1.2.`:

```sh
jq -r '[.. | objects | select(has("test_number")) | select(.status == "FAIL") | .test_number | select(startswith("1.2."))] | sort | .[]' baseline-master.json > failing-1-2.txt
```

The file `failing-1-2.txt` now holds one failing check number on each line. Keep `baseline-master.json` unchanged. After you fix settings, run the audit again into a second file and compare the two lists with `diff`. A check that disappeared from the failing list is fixed, and a check that appeared is a side effect of your change.

You can now select checks and keep results. A list of failures is only the start of a judgement, so the last question is which results a person must still decide.

## Common pitfalls

> [!WARNING]
> - **Mixing log lines with JSON.** `jq` stops at the first line that is not JSON. Keep only the document in the file.
> - **Filtering on a fixed nesting.** The depth of the document can change between versions. Walk it with `..` and select on field names.
> - **Overwriting the baseline.** Save the before result under one name and the after result under another.
> - **Rerunning one check and stopping.** After the last fix, run the full target once more.
