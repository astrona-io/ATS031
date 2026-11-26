# Read A kube-bench Check Definition — Solution

You solve this lab by reading two files from the kube-bench image with short pods, then writing one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

kube-bench keeps one directory of YAML definition files for each edition of the CIS (Center for Internet Security) Kubernetes Benchmark. Read which edition the reviewer asks for, and keep it in a variable for the next commands:

```sh
kubectl -n starfleet-031-020-02-02 get configmap audit-request -o jsonpath='{.data.edition}{"\n"}'
edition="$(kubectl -n starfleet-031-020-02-02 get configmap audit-request -o jsonpath='{.data.edition}')"
```

The value is the name of a directory such as `cis-1.10`.

## Step 2: list the definition files (check `edition-files`)

The image keeps the editions under `/opt/kube-bench/cfg`. A short pod with the image can list one directory without running an audit. The image is already on the node, so `--image-pull-policy=IfNotPresent` avoids a download:

```sh
kubectl -n starfleet-031-020-02-02 run kube-bench-files --rm -i --restart=Never --image-pull-policy=IfNotPresent --image=docker.io/aquasec/kube-bench:v0.10.6 --command -- ls "/opt/kube-bench/cfg/$edition"
```

The output has one file for each target, such as `master.yaml`, `node.yaml` and `etcd.yaml`, and a `config.yaml` file for the edition. Save the names in a local file, one on each line. The `grep -v` command removes the `pod ... deleted` line that `kubectl run --rm` can print at the end:

```sh
kubectl -n starfleet-031-020-02-02 run kube-bench-files --rm -i --restart=Never --image-pull-policy=IfNotPresent --image=docker.io/aquasec/kube-bench:v0.10.6 --command -- ls "/opt/kube-bench/cfg/$edition" | grep -v ' deleted' > edition-files.txt
cat edition-files.txt
```

## Step 3: find the API server checks (check `profiling-check-in-edition`)

Each check in `master.yaml` starts with an `id` line, followed by a `text` line. Section `1.2` holds the API server checks, section `1.3` the controller manager checks and section `1.4` the scheduler checks. Print the lines around the word `--profiling`:

```sh
kubectl -n starfleet-031-020-02-02 run kube-bench-master --rm -i --restart=Never --image-pull-policy=IfNotPresent --image=docker.io/aquasec/kube-bench:v0.10.6 --command -- cat "/opt/kube-bench/cfg/$edition/master.yaml" | grep -B2 -e 'text:.*--profiling'
```

The output shows up to three checks: one for the API server in `1.2`, one for the controller manager in `1.3` and one for the scheduler in `1.4`.

## Step 4: pick the profiling check (check `profiling-check`)

Take the `id` of the check in section `1.2`: it is the API server profiling check of this edition. Create the ConfigMap with the file list and that identifier. Replace `<CHECK_ID>` with the identifier:

```sh
kubectl -n starfleet-031-020-02-02 create configmap check-definition --from-file=files=edition-files.txt --from-literal=apiserver-profiling-check=<CHECK_ID>
```

Then check the result:

```sh
kubectl -n starfleet-031-020-02-02 get configmap check-definition -o yaml
```

The key `files` holds one file name on each line, and `apiserver-profiling-check` holds an identifier that starts with `1.2.`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not run `kube-bench run`: every check fails while a pod in the namespace runs an audit. Every check also fails when a control plane manifest or `/var/lib/kubelet/config.yaml` changed.
>
> Check numbers differ between editions, so an identifier from another edition or from memory can be wrong. The profiling check exists for three components; only the one in section `1.2` is the API server check.
>
> `kubectl run --rm -i` can add a `pod ... deleted` line to the output. Keep it out of the file list, which must equal the files of the edition exactly.
