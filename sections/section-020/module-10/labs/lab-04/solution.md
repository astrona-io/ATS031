# Report The Effective Kubelet Settings — Solution

You solve this lab by reading the effective kubelet configuration, writing one ConfigMap and changing the mode of one file. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The kubelet takes its settings from three places: its defaults, the file `/var/lib/kubelet/config.yaml`, and command-line flags. A flag overrides the file. The API server can proxy a request to the kubelet and return the merged result at the path `configz`. Read the three values from it:

```sh
kubectl get --raw "/api/v1/nodes/$(hostname)/proxy/configz" | python3 -m json.tool | grep -A2 -e '"anonymous"' -e '"authorization"' -e '"readOnlyPort"'
```

Then look at the file mode:

```sh
sudo stat -c '%a %U:%G %n' /var/lib/kubelet/config.yaml
```

The line starts with `644 root:root`, so every local user can read the file.

## Step 2: record anonymous authentication and the authorization mode (check `effective-values`)

In the `configz` output, `authentication.anonymous.enabled` is `false` and `authorization.mode` is `Webhook`. With `Webhook`, the kubelet asks the API server whether each request is allowed.

## Step 3: find the read-only port override (check `read-only-port`)

The `configz` output shows `"readOnlyPort": 10255`, but the configuration file does not set this field. Check the file and the flags file on the node to see where the value comes from:

```sh
sudo grep -i readonly /var/lib/kubelet/config.yaml
sudo cat /var/lib/kubelet/kubeadm-flags.env
```

The first command prints nothing. The second shows `--read-only-port=10255` in `KUBELET_KUBEADM_ARGS`. This flag is the override that the file review missed. The task asks you to report it, not to remove it.

Now write the three values into one ConfigMap. Save this as `configmap-kubelet-review.yaml`, with every value quoted so that it stays a string:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: kubelet-review
  namespace: starfleet-031-020-01-04
data:
  anonymous-enabled: "false"
  authorization-mode: "Webhook"
  read-only-port: "10255"
```

Apply it:

```sh
kubectl apply -f configmap-kubelet-review.yaml
```

Then check the result:

```sh
kubectl -n starfleet-031-020-01-04 get configmap kubelet-review -o yaml
```

## Step 4: restrict the configuration file (check `config-file-mode`)

The kubelet reads its configuration file when it starts, so a mode change needs no restart. Restrict the file:

```sh
sudo chmod 600 /var/lib/kubelet/config.yaml
```

## Step 5: test the result

Check the file and the node:

```sh
sudo stat -c '%a %U:%G %n' /var/lib/kubelet/config.yaml
kubectl get node "$(hostname)"
```

The `stat` line starts with `600 root:root`, and the node is `Ready`.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not fix the findings. Every check fails when the effective `readOnlyPort` is no longer `10255`, anonymous authentication is no longer `false` or the authorization mode is no longer `Webhook`, and when the node is not `Ready`.
>
> Reading only `config.yaml` misses flags such as `--read-only-port` in `kubeadm-flags.env`, and `read-only-port` would be recorded wrong. `configz` returns `readOnlyPort` only when it is not zero, so a missing field means `0`.
>
> Record values as `configz` prints them: lowercase `false`, and `Webhook` with a capital W.
