---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Authentication And Authorization Flags

Every request to the API server goes through three steps: authentication decides who the caller is, authorization decides what the caller may do, and admission can change or reject the request. The first two steps are set by flags on the API server. A weak value in either one can give an unknown caller access to the cluster. This part covers the flags that the benchmark checks, shows how to read them, and shows how to test the result with a request from an anonymous user.

## Authentication flags

Authentication turns a request into a user name and groups. If no authenticator accepts the request, the API server treats it as the user `system:anonymous` when anonymous requests are enabled. The flag `--anonymous-auth` controls this, and its default is `true`. The benchmark prefers `false`.

Setting it to `false` is not free on a kubeadm cluster. The kubelet runs health probes against the API server, and these probes send no credentials, so they rely on anonymous access to the health endpoints. Role-based access control (RBAC) denies an anonymous user everything except a small set of public endpoints such as `/healthz`, `/livez`, `/readyz` and `/version`. Newer Kubernetes versions can also limit anonymous access to chosen paths in a structured authentication configuration. Check what your version supports before you rely on it. A reviewer who sets `false` must verify that the pods of the control plane stay ready.

Other authentication flags in the benchmark are about older mechanisms. `--token-auth-file` loads static bearer tokens from a file. These tokens never expire, cannot be revoked without a restart, and sit in clear text on the node, so the benchmark asks that the flag is not set. Basic authentication with a password file was removed from Kubernetes in version 1.19. The old insecure HTTP port, `--insecure-port`, was removed in 1.24, so an exam question about it describes an old cluster. The flag `--kubelet-certificate-authority` makes the API server verify the certificate of each kubelet it connects to, which stops a fake kubelet from receiving requests.

## Authorization flags

The flag `--authorization-mode` takes a comma-separated list of authorizers, and the API server asks them in order. The value `AlwaysAllow` approves every request and fails the benchmark. The expected value is `Node,RBAC`. The `Node` authorizer limits each kubelet to the objects it needs, and `RBAC` applies the roles and bindings of the cluster. The benchmark has one check that `AlwaysAllow` is not in the list, and one check that `Node` is, and one that `RBAC` is.

## Read the flags and test anonymous access

Read the four flags in the manifest. The manifest belongs to `root`, so open a shell on the node with `astrona ssh astro-ats-031-playground-020-03` and use `sudo`. `grep` prints only lines that exist, so a flag that is absent prints nothing and the API server uses its default.

<!-- astrona:playground:renew -->

```sh
sudo grep -e '--anonymous-auth' -e '--authorization-mode' -e '--token-auth-file' -e '--kubelet-certificate-authority' /etc/kubernetes/manifests/kube-apiserver.yaml
```

The output on the playground node is one line:

```text
    - --authorization-mode=Node,RBAC
```

A kubeadm cluster sets `--authorization-mode=Node,RBAC`, and `--kubelet-certificate-authority` is absent. There is no line for `--token-auth-file`. The `--anonymous-auth` line is absent, so the default `true` applies. Next, read the same values from the mirror pod of the API server, to see what runs. The pod name is the component name followed by the node name:

```sh
kubectl -n kube-system get pod kube-apiserver-astro-ats-031-playground-020-03 -o jsonpath='{.spec.containers[0].command}'
```

The output is one long JSON list of all arguments. It contains `"--authorization-mode=Node,RBAC"` and no `--anonymous-auth` entry, so the running API server matches the file.

Now test what anonymous access really allows. A request without credentials is an anonymous request, so send one with `curl` straight to the API server on port `6443` of the node. The `-k` option skips the check of the server certificate, which is acceptable for this one test on the node itself:

```sh
curl -sk https://127.0.0.1:6443/api/v1/namespaces/kube-system/pods | grep message
curl -sk https://127.0.0.1:6443/readyz; echo
```

The output on the playground node:

```text
  "message": "pods is forbidden: User \"system:anonymous\" cannot list resource \"pods\" in API group \"\" in the namespace \"kube-system\"",
ok
```

Authentication accepted the request as the user `system:anonymous`, and RBAC then denied the list of pods with the HTTP status `403`. The health endpoint `/readyz` answers `ok`, because the ClusterRole `system:public-info-viewer` allows it for the groups `system:authenticated` and `system:unauthenticated`. This is the reason kubeadm clusters leave anonymous authentication on and still deny anonymous requests. If an anonymous request to a resource ever succeeds, someone created a binding for `system:anonymous` or for the group `system:unauthenticated`, which is a finding of its own.

You may know `kubectl auth can-i list pods --as=system:anonymous` as a way to test this. On this cluster it does not answer `no`. It fails with a `Forbidden` error, because `kubectl` sends the question as a SelfSubjectAccessReview in the name of the anonymous user, and the anonymous user may not create that object either. The error still shows that the anonymous user has no access, but the `curl` request shows the real behaviour.

The flags set who can connect and what they may do. The next control sits behind them: the admission plugins that inspect every accepted request.

## Common pitfalls

> [!WARNING]
> - **Setting `--anonymous-auth=false` without a test.** The health probes of the control plane may fail and the API server may restart in a loop. Verify readiness after the change.
> - **Reading only the manifest.** The running pod shows what the kubelet started.
> - **Treating an absent flag as safe.** The default of `--anonymous-auth` is `true`.
> - **Leaving `AlwaysAllow` in the list.** Even with `RBAC` after it, `AlwaysAllow` approves requests first.
> - **Reading a `Forbidden` error from `kubectl auth can-i --as=system:anonymous` as a broken cluster.** The anonymous user may not ask the question. Send a request without credentials with `curl` instead.
