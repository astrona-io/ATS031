# Restrict The etcd Data Directory

Someone opened the mode of the directory where etcd keeps the cluster data on the control plane node. Fix the mode and record two facts about the running etcd process in the ConfigMap `etcd-process` in namespace `starfleet-031-020-04-04`.

1. The directory in the `--data-dir` flag of the running etcd process has mode `700` or stricter and the owner `root:root`. etcd stays healthy: `kubectl get --raw=/readyz/etcd` prints `ok`.
2. Key `data-dir`: the value of `--data-dir` of the running etcd process.
3. Key `user`: the user that runs the etcd process.

Node files and processes belong to root; use `sudo`.

Do not change the owner of the data directory.
