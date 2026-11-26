# Correct The Scheduler Bind Address And Record It

A benchmark run on the control plane node reports that the kube-scheduler static pod runs with `--bind-address=0.0.0.0`, so its secure port `10259` accepts connections on every address of the node. Correct the finding (CIS check 1.4.2) and record it for the review.

1. Change `/etc/kubernetes/manifests/kube-scheduler.yaml` so the running kube-scheduler has `--bind-address=127.0.0.1` and its pod is ready again.
2. Make sure port `10259` answers on `127.0.0.1` and refuses connections on the node address.
3. Create the ConfigMap `benchmark-review` in namespace `starfleet-031-020-01-01` with `component: kube-scheduler`, `check: 1.4.2`, `setting: bind-address` and `result: corrected`.

Node files belong to root; use `sudo`. Keep any backup of the manifest outside `/etc/kubernetes/manifests`; the API server must stay ready and both `probe` replicas must stay available.
