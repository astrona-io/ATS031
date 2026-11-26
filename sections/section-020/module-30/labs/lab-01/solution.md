# Enable Audit Logging On The API Server — Solution

You solve this lab by placing one policy file and editing the API server static pod manifest. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

An audit policy tells the API server which requests to record and at which level: `None`, `Metadata`, `Request` or `RequestResponse`. The first rule that matches a request decides its level. Read the staged policy before you use it, and check that the API server has no audit flags yet:

```sh
sudo cat /opt/training/audit-policy.yaml
sudo ps -eo args | grep '^kube-apiserver' | tr ' ' '\n' | grep -e '--audit'
```

The policy skips the health paths, records Secrets only at the `Metadata` level so that the Secret values never reach the log, and records the rest at `Metadata`. The second command prints nothing.

## Step 2: place the policy and name it (check `audit-policy`)

The API server runs in a container, so it can read only the host paths that are mounted into its pod. Create the two host directories, copy the policy, and copy the manifest to a work directory outside `/etc/kubernetes/manifests`:

```sh
sudo mkdir -p /etc/kubernetes/policy /var/log/kubernetes/audit /etc/kubernetes/edit
sudo cp /opt/training/audit-policy.yaml /etc/kubernetes/policy/audit-policy.yaml
sudo cp -p /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/edit/kube-apiserver.yaml
```

The kubelet starts every file in `/etc/kubernetes/manifests` as a static pod, a pod that the kubelet runs from a file on the node. Editing a copy keeps a half-written file away from the kubelet. Open the copy with an editor:

```sh
sudo vi /etc/kubernetes/edit/kube-apiserver.yaml
```

The next three steps all change this one copy. Add this flag to the `command` list, right after the line `- kube-apiserver`, with the same indentation as the other flags:

```yaml
    - --audit-policy-file=/etc/kubernetes/policy/audit-policy.yaml
```

## Step 3: limit the log files (check `audit-log-retention`)

Add three more flags after it:

```yaml
    - --audit-log-maxage=30
    - --audit-log-maxbackup=10
    - --audit-log-maxsize=100
```

`--audit-log-maxage` keeps old log files for 30 days, `--audit-log-maxbackup` keeps at most 10 old files, and `--audit-log-maxsize` starts a new file at 100 megabytes.

## Step 4: write the log and mount the directories (check `audit-events-written`)

Add the log path flag to the `command` list as well:

```yaml
    - --audit-log-path=/var/log/kubernetes/audit/audit.log
```

Add two entries under `volumeMounts:` of the container:

```yaml
    - mountPath: /etc/kubernetes/policy
      name: audit-policy
      readOnly: true
    - mountPath: /var/log/kubernetes/audit
      name: audit-log
```

Add two entries under `volumes:` of the pod:

```yaml
  - hostPath:
      path: /etc/kubernetes/policy
      type: DirectoryOrCreate
    name: audit-policy
  - hostPath:
      path: /var/log/kubernetes/audit
      type: DirectoryOrCreate
    name: audit-log
```

Save the file, then move it back into the manifests directory in one step:

```sh
sudo mv /etc/kubernetes/edit/kube-apiserver.yaml /etc/kubernetes/manifests/kube-apiserver.yaml
```

The kubelet stops the old API server and starts a new one from the changed file.

## Step 5: test that events are written

Wait until the new API server answers:

```sh
for attempt in $(seq 1 60); do
  if sudo ps -eo args | grep '^kube-apiserver ' | grep -q -e '--audit-policy-file' && kubectl --request-timeout=3s get --raw=/readyz >/dev/null 2>&1; then echo "new flag visible and API server ready"; break; fi
  sleep 3
done
```

The old API server process can still answer for a few seconds after the `mv`, so the loop waits until the running process has the new flag and the API server is ready. It prints `new flag visible and API server ready`. If it ends without that message, run `sudo crictl ps -a --name kube-apiserver` and read the logs of the exited container with `sudo crictl logs <CONTAINER_ID>`.

Then make a request that the policy records and look for it in the log:

```sh
kubectl -n starfleet-031-020-03-01 create configmap audit-test
sudo grep -c audit-test /var/log/kubernetes/audit/audit.log
```

The `grep -c` command prints a number above zero. Each line of the log is one JSON event with the user, the verb, the resource and the response code.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Every check fails while `/etc/kubernetes/manifests` holds any file other than the four control plane manifests. A backup there becomes a second static pod.
>
> A flag without the matching volume makes the API server fail at start, because the file does not exist in its container. The policy file must have the same content as the staged policy.
>
> A retention value of `0` means no limit, not a short limit. The grader needs a number above zero for each of the three flags.
