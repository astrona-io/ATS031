# Bring A Host-Network Workload Back Under NetworkPolicy

The NetworkPolicy `starfleet-egress` in `starfleet-031-040-01-01` selects every pod and allows only DNS and TCP port 8080 to pods labelled `app: probe`. The Deployment `relay` still reaches pod `metadata-simulator` on TCP port 8080, because its pods share the network of the node.

1. Move `relay` onto the pod network, so its running pod has its own pod IP address.
2. `relay` can no longer reach `metadata-simulator` on TCP port 8080.
3. `relay` still reaches the `probe` Service at `http://probe/`.

Do not change the NetworkPolicy `starfleet-egress`, and keep `metadata-simulator` reachable from pod `drifter` in `outpost-031-040-01-01`.
