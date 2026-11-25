---
exam_objectives:
- Verify platform binaries before deploying
---
# Find The Binary That Fails Verification: Solution

Connect to the lab first, so that `kubectl` talks to this lab's cluster and `$node_name` names its control plane node:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-02-03)"
node_name="astro-ats-031-lab-050-02-03-control-plane"
```

## Why size and time do not help

Start with a listing. All seven binaries have the same size, and the same modification time:

```sh
podman exec "$node_name" ls -l --time-style=full-iso /var/lib/node-bundle
```

A change of one byte in place keeps the size, and `touch` can set any time. Only a digest of the content shows the change.

## Check every binary

Open a shell in the bundle directory on the node. The loop turns each digest-only `.sha256` file into a line in the check format and pipes it to `sha256sum --check`, which reads the line from standard input:

```sh
podman exec -it -w /var/lib/node-bundle "$node_name" bash
for binary in kube-apiserver kube-controller-manager kube-scheduler kube-proxy kubectl kubeadm kubelet; do
  printf '%s  %s\n' "$(cat $binary.sha256)" "$binary" | sha256sum --check
done
exit
```

Six lines end with `OK`. One line ends with `FAILED`, and `sha256sum` prints a warning that one computed checksum did not match.

## Record the result

The example records `kube-scheduler`; use the name from the `FAILED` line:

```sh
kubectl -n starfleet-031-050-02-03 create configmap failing-binary --from-literal=name=kube-scheduler
```

The grader computes the digest of every binary itself and compares the one that fails with the ConfigMap.
