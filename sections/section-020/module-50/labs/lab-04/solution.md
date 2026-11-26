# Close The Kubelet Read-Only Port And Raise Its TLS Minimum — Solution

You solve this lab with two fields in the kubelet configuration file and a kubelet restart. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The read-only port serves parts of the kubelet API over plain HTTP, without authentication and without authorization. Read the address of the node and send a request from the `shuttle` pod:

```sh
node_ip="$(kubectl get node "$(hostname)" -o jsonpath='{.status.addresses[?(@.type=="InternalIP")].address}')"
kubectl -n starfleet-031-020-05-04 exec shuttle -- wget -q -T 3 -O- "http://$node_ip:10255/pods" | head -c 200; echo
kubectl get --raw "/api/v1/nodes/$(hostname)/proxy/configz" | python3 -m json.tool | grep -e readOnlyPort -e tlsMinVersion
```

The first command prints the start of a JSON pod list. The effective configuration shows `readOnlyPort` `10255` and `tlsMinVersion` `VersionTLS10`.

Keep a copy of the file before you change it:

```sh
sudo cp /var/lib/kubelet/config.yaml /root/kubelet-config.yaml.before
```

## Step 2: turn off the read-only port (check `read-only-port`)

The kubelet stops at start when a key appears twice in its file, so delete the key before you add it again:

```sh
sudo sed -i '/^readOnlyPort:/d' /var/lib/kubelet/config.yaml
sudo sh -c "printf '\nreadOnlyPort: 0\n' >> /var/lib/kubelet/config.yaml"
```

`readOnlyPort: 0` turns the port off. Both edits in this lab take effect only after the kubelet restart in Step 4.

## Step 3: raise the TLS minimum (check `tls-min-version`)

`tlsMinVersion` sets the lowest TLS version that the kubelet accepts on port `10250`; TLS 1.0 and 1.1 have known weaknesses. Replace the key in the same way:

```sh
sudo sed -i '/^tlsMinVersion:/d' /var/lib/kubelet/config.yaml
sudo sh -c "printf '\ntlsMinVersion: VersionTLS12\n' >> /var/lib/kubelet/config.yaml"
sudo grep -e readOnlyPort -e tlsMinVersion /var/lib/kubelet/config.yaml
```

The `grep` command prints `readOnlyPort: 0` and `tlsMinVersion: VersionTLS12`, each once.

## Step 4: restart the kubelet (check `read-only-port-closed`)

The kubelet reads its configuration only when it starts, and only a new kubelet process stops listening on port `10255`:

```sh
sudo systemctl restart kubelet
```

## Step 5: test the result

Read the effective configuration through the API server. The `configz` endpoint returns the values that the running kubelet really uses, after all sources are merged:

```sh
kubectl get --raw "/api/v1/nodes/$(hostname)/proxy/configz" | python3 -m json.tool | grep -e readOnlyPort -e tlsMinVersion
kubectl -n starfleet-031-020-05-04 exec shuttle -- wget -q -T 3 -O- "http://$node_ip:10255/pods"; echo "exit code $?"
kubectl get node "$(hostname)"
```

`tlsMinVersion` is `VersionTLS12`. `readOnlyPort` no longer appears, because the endpoint leaves out fields with the value `0`. The `wget` command fails with an exit code other than `0`, and the node is `Ready`. If the old values still show, wait a few seconds and run the commands again.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> A second `readOnlyPort` line instead of a replaced one stops the kubelet, and a node that is not `Ready` fails every check.
>
> `readOnlyPort` missing from `configz` means `0`, not an error. A changed file without a kubelet restart leaves port `10255` open.
>
> The TLS values are names such as `VersionTLS12`, not numbers such as `1.2`. `VersionTLS11` fails the check.
