# Run The etcd Checks With A Pinned Benchmark Edition

The etcd team must report against one fixed benchmark edition, not the one that kube-bench detects. The ConfigMap `audit-request` in namespace `starfleet-031-020-02-04` names that edition under the key `benchmark`, and the image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on the node. Run their audit as the Job `etcd-audit` in the same namespace, on the control plane node.

1. Make the Job run `kube-bench run` with the target `etcd` only, and let it complete.
2. Make sure its log holds the etcd checks (section `2`) and no control plane checks (section `1`).
3. Set `--benchmark` to the edition in `audit-request`.

Create no other Job and do not change the cluster.
