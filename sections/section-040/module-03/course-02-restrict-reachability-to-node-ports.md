---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Restrict Reachability To Node Ports

A pod almost never needs to talk to a kubelet. A NetworkPolicy can close that path with the same form that blocks the metadata address: allow everything except the addresses of the nodes. This part builds that policy for the `dock` namespace, explains the port-based alternative, and states what a pod policy can and cannot protect on a node.

## The policy shape

Pods in an application namespace need DNS, other pods, Services and sometimes the internet. They do not need the addresses of the nodes. A policy that selects all pods and allows `0.0.0.0/0` except the node addresses closes the node ports, and keeps the rest open. A node address in the `except` list also blocks every other port on that node for these pods, so check that your pods do not depend on one. The API server of a kind cluster listens on the control plane node, so pods that call the Kubernetes API through the `kubernetes` Service reach a node address after Service translation. Pods that need the API server must have an explicit allow for it.

The node addresses must be exact. List them first. This command prints one internal address per line:

<!-- astrona:playground:renew -->

```sh
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.status.addresses[?(@.type=="InternalIP")].address}{"\n"}{end}'
```

Write down the address of each node. Also check that the pod network range does not overlap the node range. For this cluster the pods use a different range from the nodes, so a `/32` entry for each node cannot hit a pod.

## Apply the policy

Save this as `networkpolicy-block-node-ports.yaml`. Replace `<WORKER_IP>` and `<CONTROL_PLANE_IP>` with the addresses you wrote down:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-node-ports
  namespace: dock
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

Then check the result with a request to each kubelet port, the Service in the namespace and a control request from another namespace. Store the worker address in a variable first:

```sh
WORKER_IP=$(kubectl get nodes -l '!node-role.kubernetes.io/control-plane' -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
kubectl -n dock exec tender -- curl -sk -m 3 -o /dev/null -w '%{http_code}\n' "https://$WORKER_IP:10250/pods"
kubectl -n dock exec tender -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "http://$WORKER_IP:10255/pods"
kubectl -n dock exec tender -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe/
kubectl -n starfleet exec shuttle -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "http://$WORKER_IP:10255/pods"
```

Wait a few seconds after the apply if the first request still gets an answer. The first two requests print `000` and `kubectl` reports exit code 28, because the packets are dropped. The third prints `200`: DNS and the Service still work. The fourth prints `200`: the read-only port still answers pods in the namespace that has no policy, which proves that the block comes from the policy.

## The port-based alternative

Instead of excluding node addresses you can allow every address and every port except the kubelet ports. A NetworkPolicy has no "except these ports" field, so the form lists allowed port ranges: 1 to 10249, 10251 to 10254, and 10256 to 65535, with the fields `port` and `endPort`. The `endPort` field is stable since Kubernetes 1.25 and the network plugin must support it. Calico does. This form blocks the kubelet ports on every address in one rule, with no node list to maintain, and it breaks no other port. Its drawback is that it also blocks those ports on pods and external hosts, which may matter if an application listens on one of them. Choose the form that fits the task: when the task names the node addresses, use `ipBlock`.

## What a pod policy cannot cover

An egress policy filters traffic that leaves the pod's network interface. It does not protect the node from a process that runs on the node, and it does not apply to a pod with `hostNetwork: true`. It also does not close the port. The kubelet keeps listening, and every client that is not a selected pod can still connect, for example other machines on the node network. The durable fixes are on the node: turn the read-only port off, keep anonymous authentication off and use Webhook authorization. The network rule lowers the exposure from pods while you do that.

## Common pitfalls

> [!WARNING]
> - **Writing separate deny-list policies.** A metadata policy and a node-port policy on the same pods add up, and each one allows the address the other blocks. Put every exception in one `except` list.
> - **Guessing the node CIDR.** Read the real addresses with `kubectl get nodes -o wide`.
> - **Forgetting the control plane node.** Its kubelet answers on 10250 too.
> - **Blocking the API server by accident.** An `except` entry for a node blocks all its ports, including 6443.
> - **Judging success by one request.** Check the denied ports, a working Service and a control pod without the policy.
