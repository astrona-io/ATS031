---
exam_objectives:
- Verify platform binaries before deploying
---
# Verify The Running kubelet Against A Release Checksum: Solution

Connect to the lab first, so that `kubectl` talks to this lab's cluster and `$worker_name` names its worker node:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-02-05)"
worker_name="astro-ats-031-lab-050-02-05-worker"
```

## Do not trust the usual path

The kubelet is usually `/usr/bin/kubelet`, and `which kubelet` finds that file. But systemd starts the kubelet from the `ExecStart=` line of its unit, and a drop-in file can replace that line. Print the unit with all its drop-ins:

```sh
podman exec "$worker_name" which kubelet
podman exec "$worker_name" systemctl cat kubelet
```

The last drop-in clears `ExecStart=` and starts the kubelet from another path. The unit only says what systemd will start next time, though. The kernel knows what runs now.

## Find the running binary

`pidof` prints the process ID of the running kubelet. The link `/proc/<pid>/exe` points to the binary that the process was started from:

```sh
KUBELET_PID=$(podman exec "$worker_name" pidof kubelet)
podman exec "$worker_name" readlink /proc/$KUBELET_PID/exe
```

Use the path that `readlink` prints. `systemctl status kubelet` shows the same path in its `CGroup` lines.

## Read the version and the architecture

The node status reports the kubelet version and the CPU architecture, in the form that the release paths use:

```sh
kubectl get node "$worker_name" -o jsonpath='{.status.nodeInfo.kubeletVersion} {.status.nodeInfo.architecture}{"\n"}'
```

## Compare the digests

Compute the digest through `/proc/<pid>/exe`, so you hash exactly the bytes the process was started from. Then print the published digest for the version and the architecture. The example uses `amd64`; use your architecture:

```sh
podman exec "$worker_name" sha256sum /proc/$KUBELET_PID/exe
podman exec "$worker_name" cat /var/lib/kubelet-release/v1.35.0/bin/linux/amd64/kubelet.sha256
```

If the two digests are equal, the result is `match`. If not, it is `mismatch`. A copy with changed bytes can still start and still report `v1.35.0`, so the version alone never proves the build. Also run `sha256sum /usr/bin/kubelet`: in this lab it always gives the opposite answer, which is why checking the wrong file is a real risk.

## Record the result

Use your own values:

```sh
kubectl -n starfleet-031-050-02-05 create configmap kubelet-review \
  --from-literal=version=v1.35.0 --from-literal=path=<PATH> \
  --from-literal=sha256=<DIGEST> --from-literal=result=<match-or-mismatch>
```

The grader finds the kubelet process itself, hashes `/proc/<pid>/exe` and compares the result with the ConfigMap.
