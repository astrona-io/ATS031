# Classify Why Each Download Fails — Solution

You solve this lab by comparing digests on the node and recording the causes in one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The node of a `kind` cluster is a container on your machine. Open a shell on the control plane node (write `docker` instead of `podman` if your machine uses Docker):

```sh
podman exec -it astro-ats-031-lab-050-02-04-control-plane bash
```

Every `SOURCE` file asks for the same path, and the architecture in that path is the architecture of the node. Print it once, then print all four published digests with their paths:

```sh
cat /var/lib/k8s-incoming/batch-1/SOURCE
grep -r . /var/lib/release-index/release
```

`grep -r .` prints every line of every file under the directory with the file path in front, so each digest appears next to its version and architecture. The requested path is `release/v1.35.0/bin/linux/<architecture>/kubectl`.

For each batch you need two values: the digest of the downloaded file, which `sha256sum` computes, and the checksum that the job saved. Print both, one batch per line:

```sh
cd /var/lib/k8s-incoming
for batch in batch-1 batch-2 batch-3 batch-4 batch-5; do
  echo "$batch actual=$(sha256sum $batch/kubectl | cut -d' ' -f1) saved=$(cat $batch/kubectl.sha256)"
done
exit
```

## Step 2: find the good files (check `checksum-causes`)

Two batches have an `actual` digest equal to the published `v1.35.0` digest for the node architecture, so their file is the requested one. If `saved` equals that digest too, the batch is `ok`. If `saved` is a different value, the batch is `stale-checksum`: the file is good, but the checksum that came with it is not.

## Step 3: find the wrong files (check `failure-causes`)

Match the `actual` digest of the other three batches against the published list:

- `actual` equals the published `v1.35.0` digest for the other architecture: `wrong-arch`.
- `actual` equals the published `v1.34.4` digest for the node architecture: `wrong-version`.
- `actual` equals no published digest: `tampered`.

Look at the `tampered` batch: its `saved` checksum matches its own file. Whoever changed the file also rewrote the checksum next to it. A checksum that arrives with the file only proves the download was not damaged in transit. Only the published digest proves that the file is the published one.

## Step 4: name the rejected batch (check `rejected-download`)

The `tampered` batch is the one that must never be installed. Its name, such as `batch-3`, goes into the key `rejected`.

## Step 5: record the result (checks `checksum-causes`, `failure-causes` and `rejected-download`)

Back on your machine, replace each `<CAUSE>` with the cause you found for that batch and `<TAMPERED_BATCH>` with the name of the tampered batch. Save this as `configmap-download-triage.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: download-triage
  namespace: starfleet-031-050-02-04
data:
  batch-1: "<CAUSE>"
  batch-2: "<CAUSE>"
  batch-3: "<CAUSE>"
  batch-4: "<CAUSE>"
  batch-5: "<CAUSE>"
  rejected: "<TAMPERED_BATCH>"
```

Apply it:

```sh
kubectl apply -f configmap-download-triage.yaml
```

## Step 6: test the record

Print the ConfigMap data:

```sh
kubectl -n starfleet-031-050-02-04 get configmap download-triage -o jsonpath='{.data}{"\n"}'
```

It must show each of the five causes exactly once, one per batch, and `rejected` must name the batch marked `tampered`.

## Step 7: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not trust the `kubectl.sha256` file inside a batch. The tampered batch has a saved checksum that matches its own file, so only the published digests in `/var/lib/release-index` tell the batches apart.
>
> Do not mix up `wrong-arch` and `wrong-version`. `wrong-arch` is `v1.35.0` for the other architecture; `wrong-version` is `v1.34.4` for the node architecture.
>
> Write the causes exactly as listed, such as `stale-checksum`, and the rejected batch as `batch-3`, not as a path.
