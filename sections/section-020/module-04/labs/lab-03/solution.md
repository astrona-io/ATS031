---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Require Client Certificates On etcd Solution

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-04-03
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-04-03`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## See the problem

etcd has two ports. The client port `2379` serves the API server and other clients. The peer port `2380` serves the other members of an etcd cluster. On each port, a `*-cert-auth` flag decides whether etcd demands a client certificate that its CA has signed. Read the flags of the running process:

```sh
sudo sh -c 'tr "\0" "\n" < /proc/$(pgrep -n etcd)/cmdline' | grep -e 'cert-auth'
```

Both flags are `false`. Now send a request that has no client certificate. The `-k` option skips the check of the server certificate, so only the client side matters:

```sh
sudo curl -sk --max-time 5 https://127.0.0.1:2379/health
```

etcd answers with its health status. Any process that can reach the port can read and write data in the same way.

## Fix the manifest

The kubelet watches `/etc/kubernetes/manifests` and starts every file in it as a static pod. Edit a copy in a work directory outside that folder and move it back in one step, so that the kubelet never reads a half-written file:

```sh
sudo mkdir -p /etc/kubernetes/edit
sudo cp -p /etc/kubernetes/manifests/etcd.yaml /etc/kubernetes/edit/etcd.yaml
sudo sed -i -e 's|- --client-cert-auth=false|- --client-cert-auth=true|' -e 's|- --peer-client-cert-auth=false|- --peer-client-cert-auth=true|' /etc/kubernetes/edit/etcd.yaml
sudo grep -e 'cert-auth' /etc/kubernetes/edit/etcd.yaml
sudo mv /etc/kubernetes/edit/etcd.yaml /etc/kubernetes/manifests/etcd.yaml
```

The `grep` command shows both flags set to `true` before you move the file back.

## Check the result

The kubelet restarts etcd. During the restart the API server cannot read or write data, so wait until it is ready again:

```sh
kubectl get --raw=/readyz
sudo sh -c 'tr "\0" "\n" < /proc/$(pgrep -n etcd)/cmdline' | grep -e 'cert-auth'
sudo curl -sk --max-time 5 https://127.0.0.1:2379/health; echo "exit code $?"
```

The first command prints `ok`. Both flags are `true`. The `curl` command prints no health status and ends with an exit code other than `0`, because etcd ends the TLS handshake when the client shows no certificate.

## Common pitfalls

> [!WARNING]
> The sed pattern `--client-cert-auth=false` also matches inside `--peer-client-cert-auth=false`; check both lines after the edit. While etcd restarts, `kubectl` commands fail for a short time; wait instead of editing again. A copy of `etcd.yaml` left in `/etc/kubernetes/manifests` starts a second etcd pod.
