---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Data Directory Ownership And Permissions

TLS protects etcd on the network. The files on the disk need protection too. etcd writes its data to a directory on the node, and a user who can read that directory can copy the database without ever contacting etcd. The copy contains every Secret. This part checks the permissions and ownership of the etcd data directory and fixes a finding.

## What the directory holds

The `--data-dir` flag of etcd names the directory. kubeadm sets it to `/var/lib/etcd` and mounts it into the etcd pod as a `hostPath` volume. Inside it, the `member` directory holds a write-ahead log (WAL), which records each change before it is applied, and snapshot files of the database. A copy of these files restores the full cluster state on another machine.

The benchmark asks for two things. The directory permissions must be `700`, which means only the owner can read, write and enter the directory. The ownership should be `etcd:etcd`, a dedicated user and group, so a compromise of another account cannot read the data. The check numbers differ between editions. Find the checks by the words "data directory permissions" and "data directory ownership".

## Check the permissions

The playground widened the directory on purpose. The `stat` command prints the mode as a number, the owner and group, and the name:

<!-- astrona:playground:renew -->

```sh
NODE=astro-ats-031-playground-020-04-control-plane
podman exec $NODE stat -c '%a %U:%G %n' /var/lib/etcd
```

The mode is `755`: the owner can do everything, and every other user on the node can read and enter the directory. This is the finding. A default kubeadm node creates the directory with mode `700`, so a result of `755` shows that something changed it.

## Who runs etcd

The ownership recommendation depends on the user that runs the etcd process. Ask the node which user owns the etcd process. The host filter keeps the etcd line:

```sh
podman exec $NODE ps -eo user,args | grep '[e]tcd'
```

On a default kubeadm cluster, etcd runs as `root`, and the data directory belongs to `root:root`. The benchmark text for `etcd:etcd` assumes that a dedicated user runs etcd. On a kubeadm cluster you can create the user, change the owner of the directory and run the static pod as that user, but kubeadm does not do this by default. A reviewer therefore records the ownership finding with its reason, not as a mistake to fix with a single `chown`. If you only change the owner while etcd still runs as `root`, nothing is gained, and the change can break a restart if the process user cannot read the files.

The recommendation for permissions has no such condition. Mode `700` works with a process that runs as `root`, and you can apply it on every node.

## Fix the permissions

The fix is one command. It changes the mode of the directory, not of the files inside, because the files in `member` are already readable only by the owner on a normal installation:

```sh
podman exec $NODE chmod 700 /var/lib/etcd
podman exec $NODE stat -c '%a %U:%G %n' /var/lib/etcd
```

The second command now prints mode `700`. etcd keeps its directory open, so the running process is not restarted or interrupted. Confirm that the API server can still reach etcd through its readiness check for etcd:

```sh
kubectl get --raw='/readyz/etcd'
```

The command prints `ok`. This is the pattern for every file permission finding: read the value, change one thing, read the value again, and test the service that depends on it.

## A limit of the test in kind

A kind node is a container. Its `root` user is the root user inside the container, and the directory lives in the storage of the node container on the host. The `stat` result is correct for the container, but a review of a real server must also consider the host: who can log in, and which backup jobs copy `/var/lib/etcd`. Snapshot files you create with `etcdctl snapshot save` need the same protection as the data directory. They have the same contents.

You can now read, judge and repair the permissions of the data directory, and you know why the ownership finding needs a decision. The next question is what an attacker or reviewer actually sees when they reach etcd with a valid certificate. The next part queries the database.

## Common pitfalls

> [!WARNING]
> - **Running `chown etcd:etcd` while etcd runs as root.** It gives no protection and can stop a restart. Change the owner only together with the user of the process.
> - **Using `chmod -R 700`.** Change the data directory itself. A recursive change on other paths can break files that other components must read.
> - **Forgetting backups.** A snapshot or a copy of `/var/lib/etcd` on another path or machine holds the same secrets and needs the same protection.
> - **Judging a node by the container view.** A kind node reports the container, not the host that runs it.
