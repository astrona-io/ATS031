---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Select Checks And Export Results

A full run takes time and prints far more than you need while you fix one setting. During a fix you want to run a single check again and see only its result. At the end of a review you want a file that a script or a colleague can read. This part shows how to select checks, how to export JSON, and how to keep a baseline for a before and after comparison.

## Select checks

The `--check` option takes a comma-separated list of check numbers and runs only those. The `--group` option takes a group number, which is a block of related checks such as all of `1.2`. Because numbers differ between editions, first find the numbers in a full report, then use them in the same edition.

<!-- astrona:playground:renew -->

Open a shell on the node and run two API server checks:

```sh
astrona ssh astro-ats-031-playground-020-02
sudo kube-bench run --targets master --check 1.2.1,1.2.2
```

```text
[INFO] 1 Control Plane Security Configuration
[INFO] 1.2 API Server
[WARN] 1.2.1 Ensure that the --anonymous-auth argument is set to false (Manual)
[PASS] 1.2.2 Ensure that the --token-auth-file parameter is not set (Automated)

== Remediations master ==
1.2.1 Edit the API server pod specification file /etc/kubernetes/manifests/kube-apiserver.yaml
on the control plane node and set the below parameter.
--anonymous-auth=false


== Summary master ==
1 checks PASS
0 checks FAIL
1 checks WARN
0 checks INFO

== Summary total ==
1 checks PASS
0 checks FAIL
1 checks WARN
0 checks INFO

```

The report keeps its normal layout: check lines, remediation for the `WARN`, and a summary that counts only the two checks. A group works the same way. Group `1.4` holds the scheduler checks:

```sh
sudo kube-bench run --targets master --group 1.4 | tail -n 6
```

```text
== Summary total ==
1 checks PASS
1 checks FAIL
0 checks WARN
0 checks INFO
```

A rerun of one check has a clear job in the remediation loop: change the setting, wait for the component to restart, run only that check, and see it pass. This is faster than a full run, and it avoids reading hundreds of lines. At the end, one full run proves that the fix did not change other results.

## Export JSON

The text report is made for people. The `--json` option prints the same result as one JSON document, so a script can read it. Run the control plane audit with this option and save the output as the baseline file, the result before any fix:

```sh
sudo kube-bench run --targets master --json > baseline-master.json
jq 'keys' baseline-master.json
```

```text
[
  "Controls",
  "Totals"
]
```

Do not assume the layout of the document; look at its keys first, as here. `Controls` holds one entry per target, and `Totals` holds the counts. Each control has a list of tests, and each test has a list of results. Print the fields of one control and the counts:

```sh
jq -c '.Controls[0] | {id, version, detected_version, node_type}' baseline-master.json
jq -c '.Totals' baseline-master.json
```

```text
{"id":"1","version":"cis-1.10","detected_version":"1.35","node_type":"master"}
{"total_pass":39,"total_fail":9,"total_warn":11,"total_info":0}
```

Unlike the text report, the JSON document names the edition (`version`) and the Kubernetes version that kube-bench detected (`detected_version`). A result is an object with fields such as `test_number`, `test_desc`, `status`, `audit` and `actual_value`. The field names can change between tool versions, so check them in your file before you rely on them.

## Filter with jq

The filter below walks the whole document and picks every object that has a `test_number` and the status `FAIL`. It prints only the numbers, so it does not depend on how the controls are nested.

```sh
jq -r '[.. | objects | select(has("test_number")) | select(.status == "FAIL") | .test_number] | sort | .[]' baseline-master.json
```

```text
1.1.12
1.2.15
1.2.16
1.2.17
1.2.18
1.2.19
1.2.5
1.3.2
1.4.1
```

The `sort` of `jq` compares the numbers as text, so `1.2.5` comes after `1.2.19`. The order does not matter for a comparison, because both lists are sorted the same way. To keep only the API server checks, filter the numbers that start with `1.2.` and save them in a file:

```sh
jq -r '[.. | objects | select(has("test_number")) | select(.status == "FAIL") | .test_number | select(startswith("1.2."))] | sort | .[]' baseline-master.json > failing-1-2.txt
cat failing-1-2.txt
```

```text
1.2.15
1.2.16
1.2.17
1.2.18
1.2.19
1.2.5
```

The file `failing-1-2.txt` now holds one failing check number on each line. Keep `baseline-master.json` unchanged. After you fix settings, run the audit again into a second file and compare the two lists with `diff`. A check that disappeared from the failing list is fixed, and a check that appeared is a side effect of your change.

You can now select checks and keep results. A list of failures is only the start of a judgement, so the last question is which results a person must still decide.

## Common pitfalls

> [!WARNING]
> - **Mixing log lines with JSON.** `jq` stops at the first line that is not JSON. Do not add `--v 1` with `2>&1` to a JSON run, and keep only the document in the file.
> - **Filtering on a fixed nesting.** The depth of the document can change between versions. Walk it with `..` and select on field names.
> - **Overwriting the baseline.** Save the before result under one name and the after result under another.
> - **Saving files with `etcd` in the name.** The audits of checks `1.1.7` and `1.1.8` use an unquoted `*etcd*` pattern, which the shell matches against the current directory. A file such as `etcd.txt` in the directory where you run kube-bench makes both checks `FAIL`. Keep such files elsewhere or run kube-bench from another directory.
> - **Rerunning one check and stopping.** After the last fix, run the full target once more.
