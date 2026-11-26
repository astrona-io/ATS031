# Restore API Server Authorization And Remove Anonymous Access

A test shows that a request without any credentials can list pods. The API server allows every request, and an extra RBAC binding, whose name you are not told, grants read access to anonymous requests. Find both causes and close them.

1. Run the API server with `--authorization-mode=Node,RBAC` and without `AlwaysAllow`.
2. Remove every ClusterRoleBinding that has the subject `system:anonymous`.
3. An anonymous request (no client certificate and no token) to `https://127.0.0.1:6443/api/v1/namespaces/starfleet-031-020-03-04/pods` on the control plane node returns HTTP `401` or `403`, while `/readyz` still answers anonymous requests with `ok`.

Node files belong to root; use `sudo`. Do not set `--anonymous-auth=false`; both `probe` replicas must stay available.
