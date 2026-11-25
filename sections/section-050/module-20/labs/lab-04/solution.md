---
exam_objectives:
- Verify platform binaries before deploying
---
# Classify Why Each Download Fails: Solution

Connect to the lab first, so that `kubectl` talks to this lab's cluster and `$node_name` names its control plane node:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-02-04)"
node_name="astro-ats-031-lab-050-02-04-control-plane"
```

## Read the request and the published digests

Every `SOURCE` file asks for the same path, and the architecture in that path is the architecture of the node. Print it once, then print all four published digests with their paths:

```sh
podman exec "$node_name" cat /var/lib/k8s-incoming/batch-1/SOURCE
podman exec "$node_name" grep -r . /var/lib/release-index/release
```

`grep -r .` prints every line of every file under the directory, with the file path in front, so each digest appears next to its version and architecture.

## Compare each batch

For each batch you need two values: the digest of the downloaded file, which `sha256sum` computes, and the checksum that the job saved. Print both, one batch per line:

```sh
podman exec -it -w /var/lib/k8s-incoming "$node_name" bash
for batch in batch-1 batch-2 batch-3 batch-4 batch-5; do
  echo "$batch actual=$(sha256sum $batch/kubectl | cut -d' ' -f1) saved=$(cat $batch/kubectl.sha256)"
done
exit
```

Now match each `actual` digest against the published list:

- `actual` equals the published `v1.35.0` digest for the node architecture: if `saved` equals it too, the batch is `ok`; if not, it is `stale-checksum`. The file is good, but the saved checksum is not.
- `actual` equals the published `v1.35.0` digest for the other architecture: `wrong-arch`.
- `actual` equals the published `v1.34.4` digest for the node architecture: `wrong-version`.
- `actual` equals no published digest: `tampered`.

Look at the `tampered` batch: its `saved` checksum matches its own file. Whoever changed the file also rewrote the checksum next to it. A checksum that arrives with the file only proves the download was not damaged in transit. It does not prove the file is the published one. Only the published digest proves that.

## Record the result

The example uses one possible order; use the causes that you found:

```sh
kubectl -n starfleet-031-050-02-04 create configmap download-triage \
  --from-literal=batch-1=wrong-arch --from-literal=batch-2=ok \
  --from-literal=batch-3=tampered --from-literal=batch-4=stale-checksum \
  --from-literal=batch-5=wrong-version --from-literal=rejected=batch-3
```

The grader computes every digest itself, classifies each batch with the same rules and compares the result with the ConfigMap.
