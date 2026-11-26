# Restrict The etcd Data Directory — Solution

You solve this lab with one `chmod` on the node and one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The CIS benchmark checks the directory that etcd really uses, so read it from the running process instead of guessing the default:

```sh
sudo sh -c 'tr "\0" "\n" < /proc/$(pgrep -n etcd)/cmdline' | grep -e '^--data-dir'
```

The value is `/var/lib/etcd` on a kubeadm cluster. Now read the mode and the owner of the directory, and the user that runs etcd:

```sh
sudo stat -c '%a %U:%G %n' /var/lib/etcd
sudo ps -o user= -p "$(sudo pgrep -n etcd)"
```

The mode is `755`, so every user on the node can list the directory. The owner is `root:root`, and etcd runs as `root`.

## Step 2: restrict the mode (check `data-dir-mode`)

Change only the mode of the directory itself:

```sh
sudo chmod 700 /var/lib/etcd
```

The benchmark text asks for the owner `etcd:etcd`, which fits only when etcd runs as a user called `etcd`. Here etcd runs as `root`, so the owner stays `root:root`.

## Step 3: record the data directory (check `data-dir-recorded`)

The ConfigMap holds both facts, so create it once with both keys. The value of `data-dir` is the path you read from `--data-dir`, and the value of `user` is the user that `ps` printed:

```sh
kubectl -n starfleet-031-020-04-04 create configmap etcd-process --from-literal=data-dir=/var/lib/etcd --from-literal=user=root
```

If `--data-dir` or `ps` printed another value, use that value instead.

## Step 4: record the process user (check `process-user-recorded`)

The same command saved the key `user`. The grader compares it with the user of the newest etcd process, so it turns green together with `data-dir-recorded`.

## Step 5: test the result

Check the mode, the health of etcd through the API server and the ConfigMap:

```sh
sudo stat -c '%a %U:%G %n' /var/lib/etcd
kubectl get --raw='/readyz/etcd'; echo
kubectl -n starfleet-031-020-04-04 get configmap etcd-process -o jsonpath='{.data}'; echo
```

The first command prints `700 root:root /var/lib/etcd`. The second prints `ok`. The third shows the keys `data-dir` and `user` with the values you saved.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not run `chown etcd:etcd`. The grader requires the owner `root:root`, and a node without an `etcd` user rejects the command.
>
> A mode such as `750` still gives the group access; the grader accepts only `700` or stricter.
>
> Read the data directory and the user from the running process. The grader compares both keys with the process, not with the default path.
