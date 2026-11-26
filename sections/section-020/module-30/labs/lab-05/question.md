# Enable NodeRestriction

The security team asks what an attacker could do with the kubelet credentials of one node. Today the answer is: put any label on its own node, even the labels that should steer sensitive pods. The API server runs without the `NodeRestriction` admission plugin. Limit what a kubelet may write.

1. Run the API server with `NodeRestriction` in `--enable-admission-plugins`, and not in `--disable-admission-plugins`.
2. Keep the admission plugins that the API server enables now next to `NodeRestriction`.
3. The kubelet credentials of the node (`/etc/kubernetes/kubelet.conf`) can no longer add a label with the prefix `node-restriction.kubernetes.io/` to the node; the request is forbidden.

Node files belong to root; use `sudo`. The API server must be ready again and both `probe` replicas in `starfleet-031-020-03-05` must stay available.
