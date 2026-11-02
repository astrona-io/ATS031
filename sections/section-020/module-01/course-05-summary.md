---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Summary

The CIS Kubernetes Benchmark is a numbered list of recommendations for the control plane, etcd, worker nodes and policies. Each recommendation has a profile level and is automated or manual, and the numbers change between editions, so a review names the edition and finds a check by the setting it names. A review also depends on who owns the component: on a managed service you cannot read the control plane settings and must not report them as passed.

On a kubeadm node, the control plane runs as static pods from `/etc/kubernetes/manifests`, certificates are in `/etc/kubernetes/pki`, etcd data is in `/var/lib/etcd`, and the kubelet reads `/var/lib/kubelet/config.yaml`. `kube-bench` runs the audit of each check on the node, with targets such as `master`, `node` and `etcd`, and reports `PASS`, `FAIL`, `WARN` or `INFO`. A missing flag means the default value, which for `--profiling` is `true`. A `WARN` needs a person to decide, and a `FAIL` needs the real value on the node before any change.

The kubelet merges its configuration file, its flags and its defaults, and flags override the file. The `configz` endpoint through the API server shows the effective result. A review checks that anonymous authentication is off, that authorization is `Webhook`, that the read-only port is closed, and that the configuration files have mode `600` and owner `root`.

To correct a control plane flag, back up the manifest outside the manifests directory, change the flag in a copy, install it, wait for the pod object to show the new value, and verify that the API server is ready and the applications still answer. Record the control, the result and any exception. A single corrected control is not full compliance.

Key facts to remember:

- Find a check by the setting it names; numbers differ between editions.
- An absent flag means the default, and the default can be insecure.
- Flags override the kubelet configuration file; `configz` shows the effective values.
- Keep backups outside `/etc/kubernetes/manifests`.

<!-- astrona:playground:destroy -->
