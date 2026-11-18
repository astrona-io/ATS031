---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Read A kube-bench Check Definition Solution

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-02-02
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-02-02`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Read the requested edition

kube-bench keeps one directory of YAML definition files for each benchmark edition. Read which edition the reviewer asks for:

```sh
kubectl -n starfleet-031-020-02-02 get configmap audit-request -o jsonpath='{.data.edition}{"\n"}'
edition="$(kubectl -n starfleet-031-020-02-02 get configmap audit-request -o jsonpath='{.data.edition}')"
```

The value is the name of a directory such as `cis-1.10`. The variable `edition` keeps it for the next commands.

## List the definition files

The image keeps the editions under `/opt/kube-bench/cfg`. A short pod with the image can list one directory without running an audit. The image is already on the nodes, so `--image-pull-policy=IfNotPresent` avoids a download:

```sh
kubectl -n starfleet-031-020-02-02 run kube-bench-files --rm -i --restart=Never --image-pull-policy=IfNotPresent --image=docker.io/aquasec/kube-bench:v0.10.6 --command -- ls "/opt/kube-bench/cfg/$edition"
```

The output has one file for each target, such as `master.yaml`, `node.yaml` and `etcd.yaml`, and a `config.yaml` file for the edition. Save the names in a local file, one on each line. The `grep -v` command removes the `pod ... deleted` line that `kubectl run --rm` can print at the end:

```sh
kubectl -n starfleet-031-020-02-02 run kube-bench-files --rm -i --restart=Never --image-pull-policy=IfNotPresent --image=docker.io/aquasec/kube-bench:v0.10.6 --command -- ls "/opt/kube-bench/cfg/$edition" | grep -v ' deleted' > edition-files.txt
cat edition-files.txt
```

## Find the profiling check

Each check in `master.yaml` starts with an `id` line, followed by a `text` line. Section `1.2` holds the API server checks. Print the lines around the word `--profiling`:

```sh
kubectl -n starfleet-031-020-02-02 run kube-bench-master --rm -i --restart=Never --image-pull-policy=IfNotPresent --image=docker.io/aquasec/kube-bench:v0.10.6 --command -- cat "/opt/kube-bench/cfg/$edition/master.yaml" | grep -B2 -e 'text:.*--profiling'
```

The output shows up to three checks: one for the API server in `1.2`, one for the controller manager in `1.3` and one for the scheduler in `1.4`. Take the `id` of the check in `1.2`.

## Record the result

Create the ConfigMap with the file list and the identifier you found. Replace `<CHECK_ID>` with that identifier:

```sh
kubectl -n starfleet-031-020-02-02 create configmap check-definition --from-file=files=edition-files.txt --from-literal=apiserver-profiling-check=<CHECK_ID>
kubectl -n starfleet-031-020-02-02 get configmap check-definition -o yaml
```

## Common pitfalls

> [!WARNING]
> Check numbers differ between editions, so an identifier from another edition or from memory can be wrong. The profiling check exists for three components; only the one in section `1.2` is the API server check. `kubectl run --rm -i` can add a `pod ... deleted` line to the output; keep it out of the file list.
