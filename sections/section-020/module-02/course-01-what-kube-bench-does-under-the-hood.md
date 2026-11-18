---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# What kube-bench Does Under The Hood

A report that says `FAIL` is only useful if you know where the word came from. When a result looks wrong, the only way to judge it is to know what the tool read and what it compared. This part opens `kube-bench` and shows its three inputs: the processes on the node, the files on the node, and its own definition files for each benchmark edition.

## Checks are data, not code

`kube-bench` is a program written in Go. It does not have the benchmark rules built into its code. The rules live in YAML definition files that ship with the program, one directory for each benchmark edition. Inside an edition there is one file for each target: the control plane (`master`), the worker node (`node`), `etcd`, the control plane configuration (`controlplane`) and `policies`. A top-level file named `config.yaml` maps Kubernetes versions to editions, so the program can choose an edition by itself.

Each recommendation in a definition file is a small record. The shape below is a simplified example written for this lesson, not a copy of a real check:

```yaml
- id: 1.2.15
  text: "Ensure that the --profiling argument is set to false"
  audit: "/bin/ps -ef | grep kube-apiserver | grep -v grep"
  tests:
    test_items:
    - flag: "--profiling"
      compare:
        op: eq
        value: false
      set: true
  remediation: "Edit the API server pod specification file and set --profiling=false."
  scored: true
```

The `audit` field is a shell command. The `tests` field says how to judge the text that the command prints: which flag to find, how to compare its value, and whether the flag must be present (`set`). The `remediation` field is the text the report prints for a failing check. The `scored` field says if the result counts in the totals. The identifier in this example is only an illustration, because the numbers change between benchmark editions.

## What the audit reads

Most audit commands read one of two things. Flag checks read the arguments of a running process, such as the API server. File checks run `stat` on a file and compare its mode and owner. The program also reads the kubelet configuration file and, for some checks, asks the `kubectl` binary for objects.

This explains a requirement that surprises many learners: `kube-bench` must run where the processes and files are. Run as root on the node itself, it sees every process and file. Run in an ordinary pod, it sees only its own container. To audit a node, the pod must share the process namespace of the node (`hostPID: true`) and it must mount the host directories that the audits read, such as `/etc/kubernetes` and `/var/lib/kubelet`.

```mermaid
flowchart TB
    D["Definition file for the edition"] --> A["Audit command"]
    A -->|"reads"| P["Node processes and files"]
    P --> T["Test: compare with expected value"]
    T --> R["PASS, FAIL, WARN or INFO"]
    R --> M["Remediation text"]
```

The diagram shows that the result comes from a definition file, an audit command that reads the node, and a test that compares the output with an expected value.

## Look inside the definition files

The definition files are plain text, so you can read them without running an audit. On the playground node they are in `/etc/kube-bench/cfg`. The `kube-bench` container image keeps the same files in `/opt/kube-bench/cfg`.

<!-- astrona:playground:renew -->

Open a shell on the node and list the directories of the CIS editions:

```sh
astrona ssh astro-ats-031-playground-020-02
ls /etc/kube-bench/cfg | grep '^cis-'
```

The output is one line per edition directory:

```text
cis-1.10
cis-1.20
cis-1.23
cis-1.24
cis-1.24-microk8s
cis-1.5
cis-1.6
cis-1.6-k3s
cis-1.7
cis-1.8
cis-1.9
```

The other directories in `/etc/kube-bench/cfg` hold benchmarks for managed services and other distributions, such as `eks-1.5.0` and `gke-1.6.0`. Inside one edition there is one file for each target:

```sh
ls /etc/kube-bench/cfg/cis-1.10
```

```text
config.yaml
controlplane.yaml
etcd.yaml
master.yaml
node.yaml
policies.yaml
```

The top-level `config.yaml` holds the mapping from Kubernetes versions to editions in a block named `version_mapping`. Print the newest Kubernetes versions in that block:

```sh
grep -E '^  "1\.(2[89]|3[0-9])"' /etc/kube-bench/cfg/config.yaml
```

```text
  "1.28": "cis-1.9"
  "1.29": "cis-1.9"
  "1.30": "cis-1.10"
  "1.31": "cis-1.10"
```

The highest version in the mapping is 1.31, and the cluster runs 1.35. The mapping lags behind new Kubernetes releases, because a new benchmark edition appears after the Kubernetes version it targets. When the version is not in the mapping, kube-bench tries the next lower minor version until it finds one, so this node is judged with `cis-1.10`. The next parts return to this limit.

You now know that a result is the output of an audit command, judged by a test from a definition file for one benchmark edition. The next question is how to run the program against a node: as a binary on the node, or as a pod in the cluster.

## Common pitfalls

> [!WARNING]
> - **Running the tool in a plain pod.** Without `hostPID` and the host mounts, the audits read the container, not the node, and many checks fail for the wrong reason.
> - **Trusting a check number.** Identifiers differ between editions. Find a check by the setting it names.
> - **Assuming the tool is the benchmark.** The tool follows a definition file. If the file has a mistake or follows an older edition, the result carries the mistake.
