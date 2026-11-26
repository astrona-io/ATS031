# Require Client Certificates On etcd — Solution

You solve this lab with one edit to the etcd static pod manifest. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

etcd has two ports. The client port `2379` serves the API server and other clients. The peer port `2380` serves the other members of an etcd cluster. On each port, a `*-cert-auth` flag decides whether etcd demands a client certificate that its certificate authority (CA) has signed. Read the flags of the running process:

```sh
sudo sh -c 'tr "\0" "\n" < /proc/$(pgrep -n etcd)/cmdline' | grep -e 'cert-auth'
```

The output shows `--client-cert-auth=false` and `--peer-client-cert-auth=false`. Now send a request that has no client certificate. The `-k` option skips the check of the server certificate, so only the client side matters:

```sh
sudo curl -sk --max-time 5 https://127.0.0.1:2379/health
```

etcd answers with its health status.

## Step 2: require client certificates on the client port (check `client-cert-auth`)

The kubelet watches `/etc/kubernetes/manifests` and starts every file in it as a static pod. Edit a copy in a work directory outside that folder, so that the kubelet never reads a half-written file:

```sh
sudo mkdir -p /etc/kubernetes/edit
sudo cp -p /etc/kubernetes/manifests/etcd.yaml /etc/kubernetes/edit/etcd.yaml
sudo vi /etc/kubernetes/edit/etcd.yaml
```

In the `command` list, change the line `- --client-cert-auth=false` to:

```yaml
    - --client-cert-auth=true
```

## Step 3: require client certificates on the peer port (check `peer-client-cert-auth`)

In the same copy, change the line `- --peer-client-cert-auth=false` to:

```yaml
    - --peer-client-cert-auth=true
```

Save the file, check both lines and move the copy back in one step:

```sh
sudo grep -e 'cert-auth' /etc/kubernetes/edit/etcd.yaml
sudo mv /etc/kubernetes/edit/etcd.yaml /etc/kubernetes/manifests/etcd.yaml
```

The `grep` command shows `- --client-cert-auth=true` and `- --peer-client-cert-auth=true`.

## Step 4: wait for the new etcd process (check `anonymous-request-rejected`)

The kubelet restarts etcd. During the restart the API server cannot read or write data. The old etcd process can still answer for a few seconds after the `mv`, so wait until the running etcd process has the new flag and the API server is ready:

```sh
for attempt in $(seq 1 60); do
  if sudo ps -eo args | grep '^etcd ' | grep -q -e '--client-cert-auth=true' && kubectl --request-timeout=3s get --raw=/readyz >/dev/null 2>&1; then echo "new flag visible and API server ready"; break; fi
  sleep 3
done
```

The loop prints `new flag visible and API server ready`. If it ends without that message, run `sudo crictl ps -a --name etcd` and read the logs of the exited container.

## Step 5: test the result

Read the flags again and repeat the request without a client certificate:

```sh
sudo sh -c 'tr "\0" "\n" < /proc/$(pgrep -n etcd)/cmdline' | grep -e 'cert-auth'
sudo curl -sk --max-time 5 https://127.0.0.1:2379/health; echo "exit code $?"
kubectl get --raw=/readyz; echo
```

The first command shows both flags set to `true`. The `curl` command prints no health status and an exit code other than `0`, because etcd ends the TLS handshake when the client shows no certificate. The last command prints `ok`: the API server still reaches etcd with its own client certificate.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> A search for `--client-cert-auth=false` without the leading `- ` also matches inside `--peer-client-cert-auth=false`. Check both lines after the edit.
>
> The manifest alone does not count. The grader reads the flags of the running etcd process, so wait until the kubelet has restarted it.
>
> A copy of `etcd.yaml` left in `/etc/kubernetes/manifests` starts a second etcd pod, and the grader accepts only the four control plane manifests there.
