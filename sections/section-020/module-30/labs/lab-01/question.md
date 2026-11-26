# Enable Audit Logging On The API Server

After an incident nobody could tell who deleted a ConfigMap. The security team has staged an audit policy in `/opt/training/audit-policy.yaml` on the control plane node; no component uses it yet, and the API server writes no audit log. Turn it on.

1. Copy the staged policy unchanged to `/etc/kubernetes/policy/audit-policy.yaml`, and run the API server with `--audit-policy-file=/etc/kubernetes/policy/audit-policy.yaml`.
2. Run the API server with `--audit-log-maxage`, `--audit-log-maxbackup` and `--audit-log-maxsize`, each set to a number above zero.
3. Run the API server with `--audit-log-path=/var/log/kubernetes/audit/audit.log`, so it writes audit events to that file. Mount both host directories into the API server pod at the same paths.

Node files belong to root; use `sudo`. Keep every backup outside `/etc/kubernetes/manifests`; the API server must be ready again and both `probe` replicas must stay available.
