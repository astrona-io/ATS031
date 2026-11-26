# Find A Secret Directly In etcd

A Secret named `relay-token` exists in one namespace of the cluster; the lab does not tell you which. Use `etcdctl` against etcd, not `kubectl get secret`, to find it. Record the results in the ConfigMap `etcd-query` in namespace `starfleet-031-020-04-05`.

1. Key `secret-key`: the full etcd key of the Secret `relay-token`, in the form `/registry/secrets/<namespace>/relay-token`.
2. Key `secret-namespace`: the namespace that this key names.
3. Key `member-name`: the name of the etcd member, as `etcdctl member list` prints it.

etcd runs as a static pod on the control plane node; its image contains `etcdctl`.

Do not change or delete the Secret `relay-token`.
