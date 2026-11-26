# Correct The Scheduler Bind Address And Record It — Solution

You solve this lab with one change to the kube-scheduler static pod manifest and one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check 1.4.2 of the CIS (Center for Internet Security) Kubernetes Benchmark asks that the scheduler binds only to the loopback address `127.0.0.1`. The scheduler serves health and metrics on its secure port `10259`, and nothing outside the node needs to reach it. Read the flag of the running process:

```sh
sudo ps -eo args | grep '^kube-scheduler' | tr ' ' '\n' | grep -e '--bind-address'
```

The flag is `--bind-address=0.0.0.0`. Now test the port from the node itself, once on the loopback address and once on the node's own address. The `/healthz` path of the scheduler answers without credentials:

```sh
node_address="$(kubectl get node "$(hostname)" -o jsonpath='{.status.addresses[?(@.type=="InternalIP")].address}')"
sudo curl -sk -m 3 https://127.0.0.1:10259/healthz
sudo curl -sk -m 3 "https://$node_address:10259/healthz"
```

Both requests print `ok`. The second one shows the finding: any client that can reach the node address can reach the scheduler port.

## Step 2: change the scheduler bind address (check `scheduler-bind-address`)

The kubelet watches `/etc/kubernetes/manifests` and starts every file in it as a static pod. A static pod is a pod that the kubelet runs from a file on the node, not from the API server. So keep the backup in another directory, edit a copy, and move the copy back in one step:

```sh
sudo mkdir -p /root/backup /etc/kubernetes/edit
sudo cp -p /etc/kubernetes/manifests/kube-scheduler.yaml /root/backup/kube-scheduler.yaml
sudo cp -p /etc/kubernetes/manifests/kube-scheduler.yaml /etc/kubernetes/edit/kube-scheduler.yaml
sudo sed -i 's|--bind-address=0.0.0.0|--bind-address=127.0.0.1|' /etc/kubernetes/edit/kube-scheduler.yaml
sudo grep -e '--bind-address' /etc/kubernetes/edit/kube-scheduler.yaml
sudo mv /etc/kubernetes/edit/kube-scheduler.yaml /etc/kubernetes/manifests/kube-scheduler.yaml
```

The `sed` command changes one line of the `command` list. The `grep` line shows the new value before the kubelet sees the file:

```yaml
    - --bind-address=127.0.0.1
```

The kubelet then stops the old scheduler and starts a new one. This takes up to a minute. Read the running process and the pod again until they show the new state:

```sh
sudo ps -eo args | grep '^kube-scheduler' | tr ' ' '\n' | grep -e '--bind-address'
kubectl -n kube-system get pod "kube-scheduler-$(hostname)"
```

The flag is now `--bind-address=127.0.0.1`, and the pod is `Running` with `1/1` ready.

## Step 3: test the port (check `scheduler-loopback-only`)

The grader reads the running process, not only the file, and then connects to the port. Run the two requests from the first step again:

```sh
sudo curl -sk -m 3 https://127.0.0.1:10259/healthz
sudo curl -sk -m 3 "https://$node_address:10259/healthz"
```

The request to `127.0.0.1` still prints `ok`. The request to the node address prints nothing and fails, because nothing listens on that address any more.

## Step 4: record the decision (check `benchmark-review-record`)

A ConfigMap holds the review record as key and value pairs. Save this as `configmap-benchmark-review.yaml`:

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

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Every check fails while `/etc/kubernetes/manifests` holds any file other than the four control plane manifests. A backup such as `kube-scheduler.yaml.bak` in that directory becomes a second static pod, so keep it in `/root/backup`.
>
> A changed manifest is not a closed finding until the new process runs with the new flag. The grader reads the process, so wait for the kubelet to restart the scheduler.
>
> The ConfigMap values must match exactly. Quote the check number `"1.4.2"` in YAML so it stays a string, and spell `kube-scheduler`, `bind-address` and `corrected` as the task gives them.
