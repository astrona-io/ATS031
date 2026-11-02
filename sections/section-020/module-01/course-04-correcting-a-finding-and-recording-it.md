---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Correct A Finding Safely And Record It

A finding is only closed when the setting has changed, the component runs with the new value, and the cluster still works. Changing the API server is the risky case: it is the component that every `kubectl` command talks to, and a mistake in its manifest leaves you without a working API. This part corrects the `--profiling` finding in the API server static pod manifest, waits for the new instance, verifies the result, and records the decision.

## What happens when you edit a static pod manifest

The kubelet on the control plane node watches the directory `/etc/kubernetes/manifests`. When a file changes, the kubelet stops the pod and starts it again from the new file. While the API server restarts, `kubectl` fails with a connection error for a short time. The other control plane pods keep running and reconnect when the API server returns. The application pods in `starfleet` keep serving requests, because they do not need the API server to answer traffic.

Three rules follow. Keep every backup outside the manifests directory, because the kubelet loads every file in it as a pod. Change one flag at a time. Know the way back before you start: the original file.

## The profiling flag

The `--profiling` flag of the API server enables the `/debug/pprof` endpoints, which expose performance profiles and can be used to learn about internal state or to cause load. The default is `true`, and the benchmark recommends `false`. Before you change anything, look at what is exposed. A cluster administrator can read this endpoint through `kubectl`:

<!-- astrona:playground:renew -->

```sh
kubectl get --raw /debug/pprof/
```

With profiling enabled, the API server answers with an index of the available profiles.

## Make the change

Set the node name, take a backup in `/root` (outside the manifests directory), make a working copy, and add the flag in the working copy right below the `kube-apiserver` command. The `sed` command inserts the line `- --profiling=false` after the line `- kube-apiserver`, with the same indentation.

```sh
NODE=astro-ats-031-playground-020-01-control-plane
podman exec $NODE cp /etc/kubernetes/manifests/kube-apiserver.yaml /root/kube-apiserver.yaml.bak
podman exec $NODE cp /etc/kubernetes/manifests/kube-apiserver.yaml /root/kube-apiserver.yaml.new
podman exec $NODE sed -i 's/^    - kube-apiserver$/    - kube-apiserver\n    - --profiling=false/' /root/kube-apiserver.yaml.new
podman exec $NODE grep -n -e 'kube-apiserver$' -e 'profiling' /root/kube-apiserver.yaml.new
```

The `grep` must show the flag on the line right after `kube-apiserver`. If it shows no `profiling` line, do not install the file: the pattern did not match the indentation of your manifest. Install the new file only when the flag is in place:

```sh
podman exec $NODE cp /root/kube-apiserver.yaml.new /etc/kubernetes/manifests/kube-apiserver.yaml
```

## Wait for the new instance

The kubelet notices the change after a short delay, so the old API server can still answer for a few seconds. Do not treat an early `ok` as success. Wait until the pod object that the new instance registers shows the new flag. `kubectl` fails while the API server is down, so the loop ignores errors and tries again, at most 60 times:

```sh
for attempt in $(seq 1 60); do
  if kubectl --request-timeout=3s -n kube-system get pod kube-apiserver-$NODE -o jsonpath='{.spec.containers[0].command}' 2>/dev/null | grep -q -e '--profiling=false'; then echo "new flag visible"; break; fi
  sleep 3
done
```

Then verify three things: the API server is ready, the profiling endpoint is gone, and the application still answers.

```sh
kubectl get --raw=/readyz
kubectl get --raw /debug/pprof/
kubectl -n starfleet exec shuttle -- wget -q -T 3 -O- http://probe/
```

The first command prints `ok`. The second now fails with a `NotFound` error from the API server, because the endpoint is no longer served. The third prints the `probe` response, which proves that the application kept running. If the loop never printed the message, the API server did not start with the new manifest. Read the kubelet log on the node with `podman exec $NODE journalctl -u kubelet --no-pager -n 50`, or copy the backup back to `/etc/kubernetes/manifests/kube-apiserver.yaml` to return to the earlier state.

## Record the decision

A review needs a trail: which component, which control, and what was done. A ConfigMap is a simple form of such a record.

Save this as `configmap-benchmark-review.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: benchmark-review
  namespace: starfleet
data:
  component: kube-apiserver
  control: disable-profiling
  result: corrected
```

Apply it:

```sh
kubectl apply -f configmap-benchmark-review.yaml
```

Then check the result:

```sh
kubectl -n starfleet get configmap benchmark-review -o yaml
```

A real report also keeps the benchmark edition, the date, the value before and after, who approved the change, and the evidence of the check. For a recommendation that you decide not to follow, record the reason, the remaining risk and any control that reduces it, and give the exception a review date. After a Kubernetes upgrade the manifests are replaced and flags can change, so run the review again.

One corrected flag does not make the cluster compliant. It closes one finding. The benchmark has many more, and a passing score does not cover application code, network isolation or the supply chain of images and binaries.

## Common pitfalls

> [!WARNING]
> - **Keeping the backup in the manifests directory.** The kubelet starts a pod from every file in it. Store backups elsewhere.
> - **Declaring success too early.** The old API server may still answer. Wait for the new flag in the pod object.
> - **A wrong indentation in YAML.** The API server will not start. Compare the file with the backup before installing it.
> - **Counting one fix as compliance.** Record the single control that changed.
