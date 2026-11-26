# Find Host-Network Pods And Block New Ones

A review of `dock-031-040-03-04` and `outpost-031-040-03-04` needs to know which pods share the network of their node, and `dock-031-040-03-04` must stop accepting new ones. The existing pods keep running.

1. Create a ConfigMap `host-network-pods` in `dock-031-040-03-04` with one key, `pods`, that lists every pod in the two namespaces with `hostNetwork: true`, one `<namespace>/<pod>` per line.
2. Make `dock-031-040-03-04` enforce the `baseline` Pod Security level, so the API server rejects a new pod with `hostNetwork: true`.
3. An ordinary new pod without a `securityContext` is still accepted in `dock-031-040-03-04`.

Do not delete, recreate or change any existing pod.
