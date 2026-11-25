---
exam_objectives:
- Protect node metadata and endpoints
---
# Bring A Host-Network Workload Back Under NetworkPolicy Solution

## Confirm the gap

Store the pod IP address of `metadata-simulator` and send a request to it from the `relay` pod. The function `check` prints the HTTP status code of a request from a pod:

```sh
SIM_IP=$(kubectl -n starfleet-031-040-01-01 get pod metadata-simulator -o jsonpath='{.status.podIP}')
check() { kubectl -n "$1" exec "$2" -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "$3"; }
check starfleet-031-040-01-01 deploy/relay "http://$SIM_IP:8080/"
```

The request prints `200`, although `starfleet-egress` selects every pod with `podSelector: {}` and does not allow port 8080 of `metadata-simulator`. `kubectl exec` accepts `deploy/relay` and picks one pod of the Deployment.

## Find the cause

Compare the IP address of the `relay` pod with the IP address of its node:

```sh
kubectl -n starfleet-031-040-01-01 get pods -l app=relay -o custom-columns=NAME:.metadata.name,POD_IP:.status.podIP,HOST_IP:.status.hostIP,HOST_NETWORK:.spec.hostNetwork
```

The two addresses are the same and `HOST_NETWORK` is `true`. The pod shares the network namespace of the node, so it has no pod interface. Calico, the network plugin, enforces NetworkPolicy on the pod interface, so the policy has nothing to filter and the traffic leaves as node traffic.

## Move the workload to the pod network

Remove the field from the pod template. A JSON patch with the `remove` operation deletes exactly that field:

```sh
kubectl -n starfleet-031-040-01-01 patch deployment relay --type json -p '[{"op": "remove", "path": "/spec/template/spec/hostNetwork"}]'
kubectl -n starfleet-031-040-01-01 rollout status deployment/relay --timeout=180s
```

The Deployment controller replaces the pod. The template keeps `dnsPolicy: ClusterFirstWithHostNet`, which works like the default `ClusterFirst` for a pod on the pod network, so the pod still uses the cluster DNS. You can also run `kubectl edit deployment relay` and delete the line `hostNetwork: true`.

## Verify

Repeat the column view and the requests:

```sh
kubectl -n starfleet-031-040-01-01 get pods -l app=relay -o custom-columns=NAME:.metadata.name,POD_IP:.status.podIP,HOST_IP:.status.hostIP,HOST_NETWORK:.spec.hostNetwork
check starfleet-031-040-01-01 deploy/relay "http://$SIM_IP:8080/"
check starfleet-031-040-01-01 deploy/relay http://probe/
check outpost-031-040-01-01 drifter "http://$SIM_IP:8080/"
```

The new pod has its own pod IP address and `HOST_NETWORK` shows `<none>`. The request to `metadata-simulator` prints `000`, and `kubectl` reports exit code 28, the `curl` time-out. The request to `probe` prints `200`. The request from `drifter` prints `200`, which shows that the server still answers and that the `000` comes from the policy. Then submit.

After recording your result, remove the independent lab with `astrona destroy ats-031-lab-040-01-01`.

## Common pitfalls

> [!WARNING]
> Setting `hostNetwork: false` on the running pod is not possible, because most pod fields cannot change. Change the Deployment template and let the controller replace the pod. Adding a second NetworkPolicy does not help either: no pod policy selects a host-network pod.
