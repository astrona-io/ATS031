---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Profiling, TLS And Service Account Flags

Some API server settings are not about who may connect, but about what the server exposes and how it protects its connections and tokens. The benchmark groups several of them: profiling, the minimum TLS version, and the flags that control service account tokens. This part explains each setting, shows how to test profiling before and after the change, and finishes with the flags that you check but usually leave alone.

## Profiling

Profiling is a debugging feature. When it is on, the API server serves performance data under the path `/debug/pprof`. The data shows internals of the process, and an authorized caller can use the profiling endpoints to put load on the server. The flag `--profiling` defaults to `true`, and the benchmark asks for `false`. Production does not need the endpoint, and developers can switch it on again when they need it.

Test the endpoint before you change anything. The request goes through the API server as your administrator user.

<!-- astrona:playground:renew -->

```sh
NODE=astro-ats-031-playground-020-03-control-plane
kubectl get --raw /debug/pprof/ | head -n 5
```

With profiling on, the response is the start of an index of profile types. Now add the flag with the safe edit method: copy with `-p`, insert the flag after the line `- kube-apiserver`, move the copy into place. The `sed` command below inserts the line with the same indentation as the line it follows:

```sh
podman exec $NODE mkdir -p /etc/kubernetes/edit
podman exec $NODE cp -p /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/edit/kube-apiserver.yaml
podman exec $NODE sed -i 's|^\( *\)- kube-apiserver$|&\n\1- --profiling=false|' /etc/kubernetes/edit/kube-apiserver.yaml
podman exec $NODE mv /etc/kubernetes/edit/kube-apiserver.yaml /etc/kubernetes/manifests/kube-apiserver.yaml
until kubectl --request-timeout=3s get --raw=/readyz >/dev/null 2>&1; do sleep 3; done
```

The API server restarts, and the loop ends when it answers again. Verify in two ways. First, read the arguments of the new pod. Then repeat the request to the profiling path:

```sh
kubectl -n kube-system get pod kube-apiserver-$NODE -o jsonpath='{.spec.containers[0].command}' | tr ',' '\n' | grep profiling
kubectl get --raw /debug/pprof/ | head -n 5
```

The first command prints `--profiling=false`. The second request should now fail with a `NotFound` error, because the server no longer registers the path. If the pod object still shows the old arguments, the kubelet has not yet restarted the component. Wait and run the command again.

## TLS

The API server speaks HTTPS, and the flag `--tls-min-version` sets the lowest TLS version it accepts. Current Kubernetes versions already refuse versions below TLS 1.2 by default, but the benchmark asks you to set the value explicitly, for example `--tls-min-version=VersionTLS12`, so that the setting does not depend on a default. The flag `--tls-cipher-suites` limits the cipher suites to strong ones. Both flags are optional for a standard cluster, and a wrong cipher list can stop clients from connecting, so test with `kubectl` after a change.

Two more TLS flags are checked on the connections that the API server starts. `--client-ca-file` names the certificate authority used to verify client certificates. `--etcd-certfile`, `--etcd-keyfile` and `--etcd-cafile` set the client certificate and the authority for the connection to etcd, and the benchmark checks that they are set so that the etcd connection is authenticated.

## Service account flags

Pods authenticate to the API server with service account tokens. The API server signs these tokens with a private key and verifies them with a public key. The flags involved are `--service-account-key-file`, which names the public key used to verify tokens, `--service-account-signing-key-file`, which names the private key used to sign them, and `--service-account-issuer`, which sets the issuer name inside the token.

The flag `--service-account-lookup` makes the API server check that the service account of a token still exists in etcd. Without it, a token of a deleted service account would stay valid until the token expires. The flag defaults to `true` in current versions, and the benchmark checks that it is not `false`. Read all these flags in one command:

```sh
podman exec $NODE grep -e 'service-account' -e 'tls-' -e 'client-ca-file' -e 'etcd-' /etc/kubernetes/manifests/kube-apiserver.yaml
```

A kubeadm cluster sets the service account key flags, the client certificate authority and the etcd certificate flags. It does not set `--tls-min-version`. A check on a flag that is absent but has a secure default is a judgement call: the review states the default and decides if an explicit value is worth adding.

The flags of the API server are now covered. Two more components run beside it, and the files that hold all of them also have checks.

## Common pitfalls

> [!WARNING]
> - **Testing too early.** The pod object shows the old arguments until the kubelet restarts the component. Wait for the readiness loop.
> - **Setting `--tls-cipher-suites` without testing.** A bad list can lock out clients, including `kubectl`.
> - **Inserting the flag at the wrong indentation.** A flag with other indentation than the list items makes the YAML invalid.
> - **Calling an absent flag a failure without checking the default.** Some defaults already meet the benchmark.
