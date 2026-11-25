# Summary

The CIS Kubernetes Benchmark is a numbered list of recommended settings for the control plane, etcd, worker nodes and policies. Each recommendation has a profile level, and it is either automated or manual. The numbers change between editions, so a review names the edition it used and finds a check by the setting it names.

A review also depends on who owns the component. On a managed service you cannot read the control plane settings, so you must not report them as passed.

On a kubeadm node, the control plane runs as static pods from `/etc/kubernetes/manifests`. The certificates are in `/etc/kubernetes/pki`, the etcd data is in `/var/lib/etcd`, and the kubelet reads `/var/lib/kubelet/config.yaml`.

`kube-bench` runs the audit of each check on the node, with targets such as `master`, `node` and `etcd`. It reports `PASS`, `FAIL`, `WARN` or `INFO`. A missing flag means the default value, which for `--profiling` is `true`. A `WARN` needs a person to decide. A `FAIL` needs a look at the real value on the node before any change.

The kubelet merges its configuration file, its flags and its compiled defaults, and flags override the file. The `configz` endpoint, reached through the API server, shows the merged result. A review checks that anonymous authentication is off, that the authorization mode is `Webhook`, that the read-only port is closed, and that the configuration files have mode `600` and owner `root`.

To correct a control plane flag, you back up the manifest outside the manifests directory and change the flag in a copy. Then you install the copy, wait until the pod object shows the new value, and verify that the API server is ready and the applications still answer. Finally, you record the control, the result and any exception. A single corrected control is not full compliance.

Key facts to remember:

- Find a check by the setting it names; numbers differ between editions.
- A missing flag means the default value, and the default can be insecure.
- Flags override the kubelet configuration file; `configz` shows the effective values.
- Keep backups outside `/etc/kubernetes/manifests`.

<!-- astrona:playground:destroy -->
