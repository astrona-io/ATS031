# Harden The Controller Manager And Scheduler

A benchmark run on the control plane lists failures for the controller manager, the scheduler and the manifest files. Both components run with the profiling endpoint on (the default), and some files in `/etc/kubernetes/manifests` have mode `644`. Close these findings.

1. Run the kube-controller-manager with `--profiling=false`; its pod is ready.
2. Run the kube-scheduler with `--profiling=false`; its pod is ready.
3. Every file in `/etc/kubernetes/manifests` has mode `600` or stricter and the owner `root:root`.

Node files belong to root; use `sudo`. The API server must stay ready and both `probe` replicas in `starfleet-031-020-03-06` must stay available.
