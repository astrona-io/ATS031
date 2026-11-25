---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Guided Practice: Disable API Server Profiling In A Private Node

This ungraded playground is one virtual machine (VM) that runs a single-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-playground-020-01` is the control plane and also runs your pods. kube-bench is the tool that checks a node against the Center for Internet Security (CIS) Kubernetes Benchmark, a published list of secure settings. Its binary is in `/usr/local/bin/kube-bench`, and its benchmark files are in `/etc/kube-bench/cfg`.

Because the node is a real machine, you read and change the real static pod manifests, the kubelet files and the etcd data directory. That is the same work you do on a node in the exam.

<!-- astrona:playground:renew -->

Open a shell on the node. You log in as the `student` user, which has `sudo` and a kubeconfig file for the cluster. A kubeconfig file tells kubectl, the Kubernetes command-line tool, which cluster to use and which credentials to send.

```sh
astrona ssh astro-ats-031-playground-020-01
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-playground-020-01`. Commands that use `sudo` change only this VM. They do not touch your own computer.

## Inspect the starting state

The `starfleet` namespace has the `probe` Deployment with two pods, the `probe` Service and the `shuttle` client pod. The `outpost` namespace has the `drifter` client pod. The API server runs with the kubeadm defaults, so profiling is on.

```sh
kubectl get nodes -o wide
kubectl -n starfleet get pods -o wide
sudo kube-bench run --check 1.2.15 | grep 1.2.15
```

The node is `Ready` and runs Kubernetes `v1.35.10` with containerd `2.2.1`. The two `probe` pods and the `shuttle` pod are `Running`. kube-bench prints two lines: `[FAIL] 1.2.15 Ensure that the --profiling argument is set to false (Automated)` and the first line of the remediation text, which also contains `1.2.15`.

## The task

Set the API server flag `--profiling=false`. Create the ConfigMap `benchmark-review` in `starfleet` that records `component: kube-apiserver`, `control: disable-profiling` and `result: corrected`. Keep the API server ready and both `probe` pods available. This is one scoped configuration review, not a claim of full CIS benchmark compliance.

## Change the API server manifest

The kubelet starts the API server as a static pod from `/etc/kubernetes/manifests/kube-apiserver.yaml`. Keep the backup in `/root`, outside the manifests directory, because the kubelet starts a pod from every file in that directory. Change a working copy, and check that the flag is on the line after `- kube-apiserver`:

```sh
sudo cp /etc/kubernetes/manifests/kube-apiserver.yaml /root/kube-apiserver.yaml.bak
sudo cp /etc/kubernetes/manifests/kube-apiserver.yaml /root/kube-apiserver.yaml.new
sudo sed -i 's/^    - kube-apiserver$/    - kube-apiserver\n    - --profiling=false/' /root/kube-apiserver.yaml.new
sudo grep -n -e 'kube-apiserver$' -e 'profiling' /root/kube-apiserver.yaml.new
```

The `grep` output contains the lines `14:    - kube-apiserver` and `15:    - --profiling=false`. Install the new file only when the flag is there:

```sh
sudo cp /root/kube-apiserver.yaml.new /etc/kubernetes/manifests/kube-apiserver.yaml
```

The kubelet sees the changed file and restarts the API server. Wait until the pod object shows the new flag and the API server is ready:

```sh
for attempt in $(seq 1 60); do
  if kubectl --request-timeout=3s -n kube-system get pod kube-apiserver-astro-ats-031-playground-020-01 -o jsonpath='{.spec.containers[0].command}' 2>/dev/null | grep -q -e '--profiling=false' && kubectl --request-timeout=3s get --raw=/readyz >/dev/null 2>&1; then echo "new flag visible and API server ready"; break; fi
  sleep 3
done
```

The loop prints `new flag visible and API server ready`. On this node that took between 40 and 70 seconds.

## Record the review

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

kubectl prints `configmap/benchmark-review created`.

## Verify the result

Check that the API server is ready, that the profiling endpoint is gone, that the application still answers, and that kube-bench passes the check:

```sh
kubectl get --raw=/readyz; echo
kubectl get --raw /debug/pprof/
kubectl -n starfleet exec shuttle -- wget -q -T 3 -O- http://probe/
sudo kube-bench run --check 1.2.15 | grep 1.2.15
```

The output on this node (the pod name in `host=` differs on yours):

```text
ok
Error from server (NotFound): the server could not find the requested resource
version=v1 host=probe-7db6ffd7d6-5pkl9 greeting=hello
[PASS] 1.2.15 Ensure that the --profiling argument is set to false (Automated)
```

The `NotFound` error is the result you want: the API server no longer serves the profiling endpoint. kube-bench reads the arguments of the running process. If it still shows `[FAIL]`, the old API server process has not stopped yet; wait a few seconds and run the check again. If the loop never printed its message, read the kubelet log with `sudo journalctl -u kubelet --no-pager -n 50`, or copy `/root/kube-apiserver.yaml.bak` back into the manifests directory with `sudo cp`.

## Common pitfalls

> [!WARNING]
> Run kube-bench and every command that reads `/etc/kubernetes` with `sudo`; without root the reads fail for the wrong reason. Keep backups outside `/etc/kubernetes/manifests`. A broken edit to the API server manifest stops the API server, so kubectl fails until you fix the file. Use the benchmark edition that matches the cluster and record the control you changed: one corrected flag does not make the cluster compliant.
