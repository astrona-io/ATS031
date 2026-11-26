# Block Pod Access To The Kubelet Ports — Solution

You solve this lab with one egress NetworkPolicy that selects every pod in `outpost-031-040-03-02` and allows every address except the addresses of the two nodes. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Read the addresses of the nodes. They are the addresses you must exclude:

```sh
kubectl get nodes -o wide
worker_ip=$(kubectl get nodes -l '!node-role.kubernetes.io/control-plane' -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
control_plane_ip=$(kubectl get nodes -l 'node-role.kubernetes.io/control-plane' -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
echo "$worker_ip $control_plane_ip"
kubectl -n outpost-031-040-03-02 exec drifter -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "http://$worker_ip:10255/pods"
kubectl -n outpost-031-040-03-02 exec drifter -- curl -sk -m 3 -o /dev/null -w '%{http_code}\n' "https://$worker_ip:10250/pods"
```

The first request prints `200` because the read-only port answers without a credential. The second prints `401`, because the secure port refuses an unauthenticated request. Both prove that the ports are reachable.

## Step 2: exclude both node addresses (check `kubelet-https-port`)

The policy selects all pods with `podSelector: {}` and allows `0.0.0.0/0` except the address of each node. Both kubelets listen on port 10250, so both addresses belong in the `except` list. Replace `<WORKER_IP>` and `<CONTROL_PLANE_IP>` with the two addresses that `echo` printed.

Save this as `networkpolicy-block-node-ports.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-node-ports
  namespace: outpost-031-040-03-02
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - <WORKER_IP>/32
        - <CONTROL_PLANE_IP>/32
```

Apply it:

```sh
kubectl apply -f networkpolicy-block-node-ports.yaml
```

Wait a few seconds, then test port 10250 on both nodes:

```sh
kubectl -n outpost-031-040-03-02 exec drifter -- curl -sk -m 3 -o /dev/null -w '%{http_code}\n' "https://$worker_ip:10250/pods"
kubectl -n outpost-031-040-03-02 exec drifter -- curl -sk -m 3 -o /dev/null -w '%{http_code}\n' "https://$control_plane_ip:10250/pods"
```

Both requests print `000`, and `kubectl` reports exit code 28, the `curl` time-out.

## Step 3: confirm the read-only port is closed (check `kubelet-read-only-port`)

The worker address is excluded for every port, so the same policy also closes port 10255. The Services keep working, because the rule allows every other address:

```sh
kubectl -n outpost-031-040-03-02 exec drifter -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "http://$worker_ip:10255/pods"
kubectl -n outpost-031-040-03-02 exec drifter -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe/
kubectl -n outpost-031-040-03-02 exec drifter -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe.starfleet-031-040-03-02.svc.cluster.local/
kubectl -n starfleet-031-040-03-02 exec shuttle -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "http://$worker_ip:10255/pods"
```

The first request prints `000`. The other three print `200`: the policy exists only in `outpost-031-040-03-02`.

## Step 4: test a new pod (check `whole-namespace`)

The policy must also cover pods that start later. Start a short-lived pod with no special labels in the namespace and send a request to the read-only port from it. The options `--rm` and `-i` attach to the pod and delete it when the command ends:

```sh
kubectl -n outpost-031-040-03-02 run port-check --rm -i --restart=Never --image=docker.io/curlimages/curl:8.11.1 --command -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "http://$worker_ip:10255/pods"
```

The command prints `000`, because `podSelector: {}` selects the new pod as well. kubectl also reports that the pod `terminated (Error)`: `curl` exits with code 28 when its request times out.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Excluding only the worker address leaves port 10250 on the control plane node open. The checks test port 10250 on both nodes.
>
> A policy that selects only `app: drifter` leaves every new pod in the namespace open. The checks start a new pod without labels.
>
> Read the node addresses again if you recreate the lab, because they can change. Keep the policy in `outpost-031-040-03-02`: the checks expect `shuttle`, `tender` and `control` to still reach the read-only port.
