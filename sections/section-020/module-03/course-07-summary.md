# Summary

On a kubeadm cluster, the API server, the controller manager, the scheduler and etcd are static pods. The kubelet starts them from files in `/etc/kubernetes/manifests`, so a change to a component is a change to its file. The safe method is to copy the manifest with `cp -p` to a work directory outside the watched directory, edit the copy, and move it back in one step. Then you wait for the component and read the arguments of the running pod. Backups stay outside the manifests directory. When the API server does not start, `crictl ps -a` and `crictl logs` on the node show the cause, because `kubectl` needs the API server.

The API server flags fall into groups:

- **Access.** `--authorization-mode` must be `Node,RBAC` and never include `AlwaysAllow`. `--anonymous-auth` has the default `true`, and role-based access control (RBAC) denies anonymous requests to resources. Static token files must not be used.
- **Admission.** `NodeRestriction` limits what a kubelet can write. `AlwaysPullImages` forces a registry check on each container start. The active plugin set is the default set, plus the turned-on plugins, minus the turned-off ones.
- **Exposure.** `--profiling=false` removes the debug endpoints.
- **Connections.** The Transport Layer Security (TLS) flags set the lowest TLS version. The service account flags control how tokens are signed, verified and looked up.

Audit logging needs a policy file with ordered rules, a log path, rotation flags, and `hostPath` volumes with mounts for both the policy and the log directory. The first matching rule decides the level. Each event is one JSON line with the verb, the request address, the user and the response code.

The controller manager and the scheduler need `--profiling=false`, and the controller manager needs `--use-service-account-credentials=true`. The manifests of all control plane components should have mode `600` and owner `root:root`. After every change, the review checks the running value and the readiness of the cluster, and keeps a record of the control and the result.

Key facts to remember:

- Edit a copy outside `/etc/kubernetes/manifests`, then move it in.
- An absent flag means its default value.
- The first matching audit rule wins.
- Verify the live pod arguments, not only the file.

<!-- astrona:playground:destroy -->
