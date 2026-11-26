# Verify The Running kubelet Against A Release Checksum — Solution

You solve this lab by reading the running kubelet process on the worker node and recording four values in one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The node of a `kind` cluster is a container on your machine. Open a shell on the worker node (write `docker` instead of `podman` if your machine uses Docker):

```sh
podman exec -it astro-ats-031-lab-050-02-05-worker bash
```

The kubelet is usually `/usr/bin/kubelet`, and `which kubelet` finds that file. But systemd starts the kubelet from the `ExecStart=` line of its unit, and a drop-in file can replace that line. Print the unit with all its drop-ins:

```sh
which kubelet
systemctl cat kubelet
```

The last drop-in, `20-node-agent.conf`, clears `ExecStart=` and starts the kubelet from another path. The unit only says what systemd starts the next time, though. The kernel knows what runs now.

## Step 2: find the running binary and its version (check `kubelet-binary`)

`pidof` prints the process ID of the running kubelet. The link `/proc/<pid>/exe` points to the binary that the process was started from:

```sh
KUBELET_PID=$(pidof kubelet)
readlink /proc/$KUBELET_PID/exe
```

Use the path that `readlink` prints. It is not `/usr/bin/kubelet`.

In a second terminal on your machine, read the kubelet version and the CPU architecture from the node status. Both are already in the form that the release paths use:

```sh
kubectl get node astro-ats-031-lab-050-02-05-worker -o jsonpath='{.status.nodeInfo.kubeletVersion} {.status.nodeInfo.architecture}{"\n"}'
```

## Step 3: compute the digest of the running binary (check `kubelet-digest`)

Back in the worker shell, compute the digest through `/proc/<pid>/exe`, so you hash exactly the bytes the process was started from:

```sh
sha256sum /proc/$KUBELET_PID/exe
```

## Step 4: compare with the published digest (check `checksum-result`)

Print the published digest for the version and the architecture from Step 2. Replace `<VERSION>` and `<ARCHITECTURE>`:

```sh
cat /var/lib/kubelet-release/<VERSION>/bin/linux/<ARCHITECTURE>/kubelet.sha256; echo
exit
```

If the digest from Step 3 equals this one, the result is `match`. If not, it is `mismatch`. A copy with changed bytes can still start and still report `v1.35.0`, so the version alone never proves the build. `sha256sum /usr/bin/kubelet` always gives the opposite answer in this lab, which is why checking the wrong file is a real risk.

## Step 5: record the result (checks `kubelet-binary`, `kubelet-digest` and `checksum-result`)

Replace the placeholders with your values. Save this as `configmap-kubelet-review.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: kubelet-review
  namespace: starfleet-031-050-02-05
data:
  version: "<VERSION>"
  path: "<PATH>"
  sha256: "<DIGEST>"
  result: "<match-or-mismatch>"
```

Apply it:

```sh
kubectl apply -f configmap-kubelet-review.yaml
```

## Step 6: test the record

Print the four keys:

```sh
kubectl -n starfleet-031-050-02-05 get configmap kubelet-review -o jsonpath='{.data.version}{"\n"}{.data.path}{"\n"}{.data.sha256}{"\n"}{.data.result}{"\n"}'
```

The lines must show the version from the node status, the path from `readlink`, the digest of `/proc/<pid>/exe` and `match` or `mismatch`.

## Step 7: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not record `/usr/bin/kubelet` or its digest. The running process was started from the path in the drop-in, and `/usr/bin/kubelet` always gives the opposite result.
>
> Do not restart the kubelet or change its unit. If the kubelet no longer runs from the path in `20-node-agent.conf`, the grader fails every check.
>
> Do not decide the result from the version. A changed binary still reports `v1.35.0`; only the digest shows the change.
