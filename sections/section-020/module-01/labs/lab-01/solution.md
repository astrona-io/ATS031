---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Correct The Scheduler Bind Address And Record It Solution

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-01-01
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-01-01`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Confirm the finding

Check 1.4.2 of the benchmark asks that the scheduler binds only to the loopback address `127.0.0.1`. The scheduler serves health and metrics on its secure port `10259`, and nothing outside the node needs to reach it. First, read the flag of the running process:

```sh
sudo ps -eo args | grep '^kube-scheduler' | tr ' ' '\n' | grep -e '--bind-address'
```

The flag is `--bind-address=0.0.0.0`. Now test the port from the node itself, once on the loopback address and once on the node's own address. The `/healthz` path of the scheduler answers without credentials:

```sh
node_address="$(kubectl get node "astro-ats-031-lab-020-01-01" -o jsonpath='{.status.addresses[?(@.type=="InternalIP")].address}')"
sudo curl -sk -m 3 https://127.0.0.1:10259/healthz
sudo curl -sk -m 3 "https://$node_address:10259/healthz"
```

Both requests print `ok`. The second one shows the finding: any client that can reach the node address can reach the scheduler port.

## Change the manifest safely

The kubelet watches `/etc/kubernetes/manifests` and starts every file in it as a static pod. So keep the backup in another directory, edit a copy, and move the copy back in one step:

```sh
sudo mkdir -p /root/backup /etc/kubernetes/edit
sudo cp -p /etc/kubernetes/manifests/kube-scheduler.yaml /root/backup/kube-scheduler.yaml
sudo cp -p /etc/kubernetes/manifests/kube-scheduler.yaml /etc/kubernetes/edit/kube-scheduler.yaml
sudo sed -i 's|--bind-address=0.0.0.0|--bind-address=127.0.0.1|' /etc/kubernetes/edit/kube-scheduler.yaml
sudo grep -e '--bind-address' /etc/kubernetes/edit/kube-scheduler.yaml
sudo mv /etc/kubernetes/edit/kube-scheduler.yaml /etc/kubernetes/manifests/kube-scheduler.yaml
```

The `grep` line shows the new value before the kubelet sees the file. The kubelet then stops the old scheduler and starts a new one. This takes up to a minute.

## Verify the running process

Run the checks from the start again until they show the new state:

```sh
sudo ps -eo args | grep '^kube-scheduler' | tr ' ' '\n' | grep -e '--bind-address'
sudo curl -sk -m 3 https://127.0.0.1:10259/healthz
sudo curl -sk -m 3 "https://$node_address:10259/healthz"
kubectl -n kube-system get pod "kube-scheduler-astro-ats-031-lab-020-01-01"
```

The flag is now `--bind-address=127.0.0.1`. The request to `127.0.0.1` still prints `ok`, and the request to the node address fails because nothing listens there. The pod is `Running` and ready.

## Record the decision

Save this as `configmap-benchmark-review.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: benchmark-review
  namespace: starfleet-031-020-01-01
data:
  component: kube-scheduler
  check: "1.4.2"
  setting: bind-address
  result: corrected
```

Apply it:

```sh
kubectl apply -f configmap-benchmark-review.yaml
```

Then check the result:

```sh
kubectl -n starfleet-031-020-01-01 get configmap benchmark-review -o yaml
```

## Common pitfalls

> [!WARNING]
> A backup inside `/etc/kubernetes/manifests` becomes a second static pod. A changed manifest is not a closed finding until the new process runs with the new flag, so read the process, not only the file. Quote the check number `"1.4.2"` in YAML.
