# Bring A Host-Network Workload Back Under NetworkPolicy — Solution

You solve this lab by removing one field from the `relay` Deployment, so the existing policy applies to its pod. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Store the pod IP address of `metadata-simulator` and send a request to it from `relay`. The function `http_status` prints the HTTP status code of a request from a pod:

```sh
simulator_ip=$(kubectl -n starfleet-031-040-01-01 get pod metadata-simulator -o jsonpath='{.status.podIP}')
http_status() { kubectl -n "$1" exec "$2" -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "$3"; }
http_status starfleet-031-040-01-01 deploy/relay "http://$simulator_ip:8080/"
```

The request prints `200`, although `starfleet-egress` selects every pod with `podSelector: {}` and does not allow port 8080 of `metadata-simulator`. `kubectl exec` accepts `deploy/relay` and picks one pod of the Deployment.

Compare the IP address of the `relay` pod with the IP address of its node:

```sh
kubectl -n starfleet-031-040-01-01 get pods -l app=relay -o custom-columns=NAME:.metadata.name,POD_IP:.status.podIP,HOST_IP:.status.hostIP,HOST_NETWORK:.spec.hostNetwork
```

The two addresses are the same and `HOST_NETWORK` is `true`. The pod shares the network namespace of the node, so it has no pod interface. Calico, the network plugin, enforces NetworkPolicy on the pod interface, so the policy has nothing to filter and the traffic leaves as node traffic.

## Step 2: move relay onto the pod network (check `pod-network`)

Remove the field from the pod template. A JSON patch with the `remove` operation deletes exactly that field:

```sh
kubectl -n starfleet-031-040-01-01 patch deployment relay --type json -p '[{"op": "remove", "path": "/spec/template/spec/hostNetwork"}]'
kubectl -n starfleet-031-040-01-01 rollout status deployment/relay --timeout=180s
```

The Deployment controller replaces the pod, because most fields of a running pod cannot change. The template keeps `dnsPolicy: ClusterFirstWithHostNet`, which works like the default `ClusterFirst` for a pod on the pod network, so the pod still uses the cluster DNS. Repeat the column view:

```sh
kubectl -n starfleet-031-040-01-01 get pods -l app=relay -o custom-columns=NAME:.metadata.name,POD_IP:.status.podIP,HOST_IP:.status.hostIP,HOST_NETWORK:.spec.hostNetwork
```

The new pod has its own pod IP address, and `HOST_NETWORK` shows `<none>`.

## Step 3: confirm the metadata path is closed (check `metadata-blocked`)

Now the pod has a pod interface, and `starfleet-egress` filters it. The policy allows no traffic to `metadata-simulator`:

```sh
http_status starfleet-031-040-01-01 deploy/relay "http://$simulator_ip:8080/"
http_status outpost-031-040-01-01 drifter "http://$simulator_ip:8080/"
```

The request from `relay` prints `000`, and `kubectl` reports exit code 28, the `curl` time-out. The request from `drifter` prints `200`, which shows that the server still answers and that the `000` comes from the policy.

## Step 4: confirm the allowed path still works (check `probe-reachable`)

The policy allows DNS to CoreDNS and TCP port 8080 to the pods labelled `app: probe`. The Service `probe` sends port 80 to port 8080 of those pods, so a request by name still works:

```sh
http_status starfleet-031-040-01-01 deploy/relay http://probe/
```

The request prints `200`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Change the Deployment template, not the running pod. The checks read `hostNetwork` in the template and in the running pod, and they reject a pod whose pod IP address equals the IP address of its node.
>
> Do not change `starfleet-egress` and do not add a policy to block the metadata path. No pod policy selects a host-network pod, and the checks compare `starfleet-egress` with its starting spec.
>
> Wait for the rollout to finish. The checks need exactly one running `relay` pod and a Deployment with all replicas updated and available.
