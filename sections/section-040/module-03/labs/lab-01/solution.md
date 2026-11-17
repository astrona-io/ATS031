---
exam_objectives:
- Protect node metadata and endpoints
---
# Close The Kubelet Read-Only Port Solution

## Inspect the starting state

Store the name and address of the worker node, then confirm that the read-only port answers. The request goes from the `inspector` pod to the worker's address:

```sh
WORKER=$(kubectl get nodes -l '!node-role.kubernetes.io/control-plane' -o jsonpath='{.items[0].metadata.name}')
WORKER_IP=$(kubectl get nodes -l '!node-role.kubernetes.io/control-plane' -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
kubectl -n dock-031-040-03-01 exec inspector -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "http://$WORKER_IP:10255/pods"
kubectl get --raw "/api/v1/nodes/$WORKER/proxy/configz" | grep -o '"readOnlyPort":[0-9]*'
```

The request prints `200`: the kubelet sends the pod list to a caller with no credential. The second command asks the API server for the configuration that the running kubelet uses, and it prints `"readOnlyPort":10255`.

## Change the kubelet configuration

The kubelet reads `/var/lib/kubelet/config.yaml` only when it starts. Set the port to `0` in the file on the worker, then restart the kubelet with `systemctl`. Use `docker` instead of `podman` if your machine uses Docker:

```sh
podman exec astro-ats-031-lab-040-03-01-worker sed -i 's/^readOnlyPort:.*/readOnlyPort: 0/' /var/lib/kubelet/config.yaml
podman exec astro-ats-031-lab-040-03-01-worker grep readOnlyPort /var/lib/kubelet/config.yaml
podman exec astro-ats-031-lab-040-03-01-worker systemctl restart kubelet
```

The `grep` command prints `readOnlyPort: 0`. Deleting the whole line also works, because the kubelet turns the port off when the field is missing from a configuration file.

## Verify

Wait until the node is `Ready` again, then check the running configuration and both ports:

```sh
kubectl wait --for=condition=Ready "node/$WORKER" --timeout=120s
kubectl get --raw "/api/v1/nodes/$WORKER/proxy/configz" | grep -o '"readOnlyPort":[0-9]*'
kubectl -n dock-031-040-03-01 exec inspector -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "http://$WORKER_IP:10255/pods"
kubectl -n dock-031-040-03-01 exec inspector -- curl -sk -m 3 -o /dev/null -w '%{http_code}\n' "https://$WORKER_IP:10250/pods"
```

The `grep` on the running configuration finds no match, because the kubelet leaves out a port of `0`. The request to port 10255 prints `000`, because nothing listens on the port any more. The request to port 10250 prints `401`: the secure port still runs and still refuses a caller without a credential.

After recording your result, remove the independent lab with `astrona destroy ats-031-lab-040-03-01`.

## Common pitfalls

> [!WARNING]
> Editing the file without restarting the kubelet changes nothing on the running node: the read-only port keeps answering until the kubelet restarts. A typing mistake in `/var/lib/kubelet/config.yaml` stops the kubelet from starting, and the node turns `NotReady`; read `journalctl -u kubelet` on the worker to find the line. A NetworkPolicy that blocks port 10255 hides the port from some pods, but the kubelet still serves it to every other caller.
