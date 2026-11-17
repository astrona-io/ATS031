---
exam_objectives:
- Verify platform binaries before deploying
---
# Pick The Release Files For A Node: Solution

Connect to the lab first, so that `kubectl` talks to this lab's cluster and `$node_name` names its control plane node:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-02-01)"
node_name="astro-ats-031-lab-050-02-01-control-plane"
MIRROR=/var/lib/k8s-mirror
```

## Find the stable version

The release site has no `latest` directory. The file `release/stable.txt` holds the version of the current stable release. List the release directory to see what else is there:

```sh
podman exec "$node_name" ls $MIRROR/release
podman exec "$node_name" cat $MIRROR/release/stable.txt
```

The listing also shows `latest.txt`, which names a pre-release (`alpha`), and one `stable-1.<minor>.txt` file for each minor version. Neither is the current stable release. Use the version in `stable.txt`.

## Find the architecture of the worker

The Kubernetes API reports the architecture of every node in the node status, already in the form that the release paths use:

```sh
kubectl get nodes -o custom-columns=NAME:.metadata.name,ARCH:.status.nodeInfo.architecture
```

You can also run `uname -m` in the worker node container. It prints `x86_64` for `amd64` and `aarch64` for `arm64`.

## Build the path and read the digest

Put the version and the architecture into the path. The example uses `v1.34.3` and `arm64`; use your own values:

```sh
podman exec "$node_name" ls $MIRROR/release/v1.34.3/bin/linux/arm64
podman exec "$node_name" cat $MIRROR/release/v1.34.3/bin/linux/arm64/kubeadm.sha256
```

The `.sha256` file holds only the 64-character digest, with no file name.

## Record the result

```sh
kubectl -n starfleet-031-050-02-01 create configmap release-pick \
  --from-literal=path=release/v1.34.3/bin/linux/arm64/kubeadm \
  --from-literal=sha256=<DIGEST>
```

Replace `<DIGEST>` with the content of the `.sha256` file. The grader reads `stable.txt` and the architecture of the worker itself, builds the path and compares both values.
