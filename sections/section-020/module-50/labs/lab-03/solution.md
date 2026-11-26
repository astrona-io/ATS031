# Remove A Kubelet Flag That Overrides The Configuration File — Solution

You solve this lab by removing one flag from the kubelet flags file and restarting the kubelet. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The kubelet takes its settings from three places: the configuration file, command-line flags and built-in defaults. A command-line flag wins over the file. Read the effective value first, then the file:

```sh
kubectl get --raw "/api/v1/nodes/$(hostname)/proxy/configz" | python3 -m json.tool | grep -A2 '"authorization"'
sudo grep -A1 '^authorization:' /var/lib/kubelet/config.yaml
```

The effective mode is `AlwaysAllow`, so the kubelet allows every request that passes authentication. The file says `Webhook`, so something else sets the value.

systemd starts the kubelet. Its unit and the kubeadm drop-in file name the command line and the environment files that it reads:

```sh
sudo systemctl cat kubelet
sudo cat /var/lib/kubelet/kubeadm-flags.env
```

The drop-in file reads `/var/lib/kubelet/kubeadm-flags.env`, and the variable `KUBELET_KUBEADM_ARGS` in it holds `--authorization-mode=AlwaysAllow` as its first flag.

## Step 2: remove the flag from the flags file (check `flags-file-clean`)

Keep a copy, then remove only the flag and the space after it:

```sh
sudo cp /var/lib/kubelet/kubeadm-flags.env /root/kubeadm-flags.env.before
sudo sed -i 's|--authorization-mode=AlwaysAllow ||' /var/lib/kubelet/kubeadm-flags.env
sudo cat /var/lib/kubelet/kubeadm-flags.env
```

The line still starts with `KUBELET_KUBEADM_ARGS="` and keeps every other flag; only `--authorization-mode=AlwaysAllow` is gone.

## Step 3: restart the kubelet (check `kubelet-flag-removed`)

systemd reads the environment file only when it starts the kubelet, so the running process still has the old flag. Restart it and read the command line of the new process:

```sh
sudo systemctl restart kubelet
sudo sh -c 'tr "\0" "\n" < /proc/$(pgrep -n kubelet)/cmdline' | grep -e authorization
```

The `grep` command prints no `--authorization-mode` line.

## Step 4: check the effective mode (check `webhook-effective`)

Without the flag, the value from the configuration file applies. Read the effective configuration through the API server. The `configz` endpoint returns the values that the running kubelet really uses, after all sources are merged:

```sh
kubectl get --raw "/api/v1/nodes/$(hostname)/proxy/configz" | python3 -m json.tool | grep -A2 '"authorization"'
kubectl get node "$(hostname)"
```

The mode is now `Webhook`, so the kubelet asks the API server with a `SubjectAccessReview` whether each caller may do the request. The node is `Ready`. If the old value still shows, wait a few seconds and read it again, because the endpoint answers from the new kubelet only after it has started.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Editing only `config.yaml` changes nothing when a flag overrides the value. The grader checks the flags file, the running process and the effective value.
>
> Removing the whole `KUBELET_KUBEADM_ARGS` line also removes the other flags, such as the container runtime endpoint, and the kubelet fails. A node that is not `Ready` fails every check.
>
> A changed flags file without a kubelet restart leaves the flag on the running process.
