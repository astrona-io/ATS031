# Find The Binary That Fails Verification — Solution

You solve this lab with one `sha256sum` loop on the node and one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The node of a `kind` cluster is a container on your machine. Open a shell on the control plane node (write `docker` instead of `podman` if your machine uses Docker):

```sh
podman exec -it astro-ats-031-lab-050-02-03-control-plane bash
```

List the bundle with full timestamps:

```sh
cd /var/lib/node-bundle
ls -l --time-style=full-iso
```

All seven binaries have the same size and the same modification time. A change of one byte in place keeps the size, and `touch` can set any time. Only a digest of the content shows the change.

## Step 2: verify every binary (checks `binary-name` and `failing-binary`)

The loop turns each digest-only `.sha256` file into a line in the check format (digest, two spaces, file name) and pipes it to `sha256sum --check`, which reads the line from standard input:

```sh
for binary in kube-apiserver kube-controller-manager kube-scheduler kube-proxy kubectl kubeadm kubelet; do
  printf '%s  %s\n' "$(cat $binary.sha256)" "$binary" | sha256sum --check
done
exit
```

Six lines end with `OK`. One line ends with `FAILED`, and `sha256sum` prints a warning that one computed checksum did not match. The name in front of `: FAILED` is the answer.

## Step 3: record the result (checks `failing-record`, `binary-name` and `failing-binary`)

Back on your machine, replace `<BINARY>` with the name from the `FAILED` line. Save this as `configmap-failing-binary.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: failing-binary
  namespace: starfleet-031-050-02-03
data:
  name: "<BINARY>"
```

Apply it:

```sh
kubectl apply -f configmap-failing-binary.yaml
```

## Step 4: test the record

Print the key:

```sh
kubectl -n starfleet-031-050-02-03 get configmap failing-binary -o jsonpath='{.data.name}{"\n"}'
```

It must print the name from the `FAILED` line of Step 2, such as `kube-scheduler`, with nothing in front of it.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not pick the binary by size or by time with `ls -l`. Every binary has the same size and the same time; only the digest shows the change.
>
> Write only the file name, such as `kubeadm`. A path like `/var/lib/node-bundle/kubeadm` or a name with `.sha256` fails the check.
>
> Do not change a binary or a `.sha256` file to make the check pass. The grader then finds more or fewer than one failing binary and fails every check.
