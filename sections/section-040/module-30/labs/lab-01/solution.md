# Close The Kubelet Read-Only Port — Solution

You solve this lab by changing one line in the kubelet configuration file on the worker and restarting the kubelet. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Store the name and address of the worker node, then confirm that the read-only port answers. The request goes from the `inspector` pod to the address of the worker:

```sh
worker=$(kubectl get nodes -l '!node-role.kubernetes.io/control-plane' -o jsonpath='{.items[0].metadata.name}')
worker_ip=$(kubectl get nodes -l '!node-role.kubernetes.io/control-plane' -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
kubectl -n dock-031-040-03-01 exec inspector -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "http://$worker_ip:10255/pods"
kubectl get --raw "/api/v1/nodes/$worker/proxy/configz" | grep -o '"readOnlyPort":[0-9]*'
```

The request prints `200`: the kubelet sends the pod list to a caller with no credential. The second command asks the API server for the configuration that the running kubelet uses, and it prints `"readOnlyPort":10255`.

## Step 2: change the configuration file (check `config-closed`)

The kubelet reads `/var/lib/kubelet/config.yaml` only when it starts. Open the file on the worker and change the line `readOnlyPort: 10255` to:

```yaml
readOnlyPort: 0
```

The `sed` command below makes exactly that edit. Use `docker` instead of `podman` if your machine uses Docker:

```sh
podman exec astro-ats-031-lab-040-03-01-worker sed -i 's/^readOnlyPort:.*/readOnlyPort: 0/' /var/lib/kubelet/config.yaml
podman exec astro-ats-031-lab-040-03-01-worker grep readOnlyPort /var/lib/kubelet/config.yaml
```

The `grep` command prints `readOnlyPort: 0`. Deleting the whole line also works, because the kubelet turns the port off when the field is missing from a configuration file.

## Step 3: restart the kubelet (check `kubelet-restarted`)

The running kubelet still uses the old value. Restart it with `systemctl`, then wait until the node is `Ready` again:

```sh
podman exec astro-ats-031-lab-040-03-01-worker systemctl restart kubelet
kubectl wait --for=condition=Ready "node/$worker" --timeout=120s
kubectl get --raw "/api/v1/nodes/$worker/proxy/configz" | grep -o '"readOnlyPort":[0-9]*'
```

The node can still show `Ready` from before the restart for a few seconds. If a command fails with `connect: connection refused`, the kubelet is still starting; wait a few seconds and run it again. The `grep` on the running configuration then finds no match, because the kubelet leaves out a port of `0`.

## Step 4: test both ports (check `port-closed`)

Send the request to the read-only port again, and one to the HTTPS port:

```sh
kubectl -n dock-031-040-03-01 exec inspector -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "http://$worker_ip:10255/pods"
kubectl -n dock-031-040-03-01 exec inspector -- curl -sk -m 3 -o /dev/null -w '%{http_code}\n' "https://$worker_ip:10250/pods"
```

The request to port 10255 prints `000`, and `kubectl` adds `command terminated with exit code 7`: curl could not connect, because nothing listens on the port any more. The request to port 10250 prints `401`: the secure port still runs and still refuses a caller without a credential.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Editing the file without restarting the kubelet changes nothing on the running node. The checks read the running configuration through the API server, and the read-only port keeps answering until the kubelet restarts.
>
> A typing mistake in `/var/lib/kubelet/config.yaml` stops the kubelet from starting, and the node turns `NotReady`. Every check needs a `Ready` worker and a `401` from port 10250; read `journalctl -u kubelet` on the worker to find the line.
>
> A NetworkPolicy that blocks port 10255 hides the port from some pods, but the kubelet still serves it to every other caller, and the running configuration still shows the port.
