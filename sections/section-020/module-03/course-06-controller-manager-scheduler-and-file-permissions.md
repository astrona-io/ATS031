---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Controller Manager, Scheduler And File Permissions

The API server is not the only control plane component with checks. The controller manager runs the control loops that keep the cluster in its desired state, and the scheduler assigns pods to nodes. Both have a few settings in the benchmark. The files that hold the manifests and certificates of all components also have checks, and they are often the quickest failures to fix. This part covers the component flags and the file permissions, and ends with how to apply the changes.

## Controller manager flags

The controller manager has these checks:

- `--profiling=false` turns off the debugging endpoint, as for the API server.
- `--use-service-account-credentials=true` makes each controller run with its own service account instead of one shared identity. RBAC rules and audit events can then tell the controllers apart.
- `--service-account-private-key-file` names the key that signs service account tokens. It must be set so that tokens can be issued.
- `--root-ca-file` names the certificate authority bundle that is placed in each service account, so pods can verify the API server.
- `--bind-address=127.0.0.1` keeps the secure port of the manager on the loopback address.
- `--terminated-pod-gc-threshold` sets how many terminated pods are kept before they are deleted.

A kubeadm cluster already sets the key file, the root certificate file and `--use-service-account-credentials=true`. It also sets the bind address to `127.0.0.1`. Profiling is the setting that usually fails.

## Scheduler flags

The scheduler has two checks that matter: `--profiling=false`, and `--bind-address=127.0.0.1`. The scheduler has no other secret to protect, so these are quick to read and fix.

## File permissions

The static pod manifests hold the exact flags of each component. A user who can write them can change the cluster. The benchmark asks that the manifests have mode `600` or stricter and are owned by `root:root`. The same applies to the kubeconfig files of the components in `/etc/kubernetes`. The directory `/etc/kubernetes/pki` should be owned by `root`. Keys in it should be mode `600`. Certificates are created by kubeadm with mode `644`, and the benchmark editions differ in what they ask for them, so read the audit text of your edition.

Show the current state of the manifests in the playground, where the three control plane manifests were widened on purpose:

<!-- astrona:playground:renew -->

```sh
NODE=astro-ats-031-playground-020-03-control-plane
podman exec $NODE stat -c '%a %U:%G %n' /etc/kubernetes/manifests/etcd.yaml /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/manifests/kube-controller-manager.yaml /etc/kubernetes/manifests/kube-scheduler.yaml
podman exec $NODE stat -c '%a %U:%G %n' /etc/kubernetes/admin.conf /etc/kubernetes/controller-manager.conf /etc/kubernetes/scheduler.conf
```

The first listing shows mode `600` for `etcd.yaml` and `644` for the other three. The second listing shows the kubeconfig files. Now fix the three widened manifests. A mode change does not change the content, so no copy is needed:

```sh
podman exec $NODE chown root:root /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/manifests/kube-controller-manager.yaml /etc/kubernetes/manifests/kube-scheduler.yaml
podman exec $NODE chmod 600 /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/manifests/kube-controller-manager.yaml /etc/kubernetes/manifests/kube-scheduler.yaml
```

The kubelet runs as `root`, so it can still read the files. Verify with `stat` again, then check that the three components are still ready:

```sh
podman exec $NODE stat -c '%a %U:%G %n' /etc/kubernetes/manifests/*.yaml
kubectl -n kube-system get pods -l tier=control-plane
```

All four files should now show `600 root:root`, and the pods should stay `Running`. A change of attributes can make the kubelet look at the file again, so a brief restart of a component is possible. The pods return to ready without further action.

## Apply the component flags

To add `--profiling=false` to the controller manager and the scheduler, copy each manifest with `cp -p` to `/etc/kubernetes/edit`, edit the copy and move it back, with the `sed` insert that follows the first command line. For the controller manager, insert after `- kube-controller-manager`, and for the scheduler, after `- kube-scheduler`. Move the copy back, then read the new pod arguments. Since a copy made with `cp -p` keeps the mode, the fixed permissions stay.

The most common failure at this point is a manifest whose copy lost its mode, so always check `stat` after the final move.

You have now seen each kind of change that the benchmark asks for on the control plane: flags in a manifest, new volumes, and file attributes. The point of each change is a verified value on the running component, not a changed file.

## Common pitfalls

> [!WARNING]
> - **Losing the mode in a copy.** A plain `cp` or a redirect from `sed` can create a file with mode `644`. Use `cp -p` and check with `stat`.
> - **Making a file unreadable to the kubelet.** Use owner `root` and mode `600`, not another owner.
> - **Fixing only the API server.** The controller manager and the scheduler have their own profiling flag.
> - **Stopping at the file.** Confirm that the component runs with the new value and stays ready.
