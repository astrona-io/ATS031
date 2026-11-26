# Run The Node Checks With A kube-bench Job

The cluster has a control plane report, but nobody has run the worker node checks of the benchmark on its node yet. Run that audit. The image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on the node.

1. Create the Job `node-audit` in namespace `starfleet-031-020-02-03` that runs `kube-bench run --targets node` with the image `docker.io/aquasec/kube-bench:v0.10.6`, and let it complete.
2. Make sure the log of its pod holds the kubelet results of section `4.2` of the benchmark.
3. Run the pod on the node of the cluster with `hostPID: true`, so it shares the process namespace of the node, and mount the node directories that the audit reads.

Create no other Job and do not change the cluster.
