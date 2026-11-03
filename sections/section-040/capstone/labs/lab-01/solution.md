---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Protect The Node Solution

The task has four results. Policies add up, so the key decision is how to combine the metadata and kubelet rules. Two separate deny-list policies would cancel each other for every pod in the namespace, because the metadata policy allows the node addresses and the node policy allows the metadata address. The union allows both. One policy per namespace must carry every exception in a single `except` list.

## Inspect the starting state

Store the node addresses and the helper function, then confirm that every path is open:

```sh
WORKER_IP=$(kubectl get nodes -l '!node-role.kubernetes.io/control-plane' -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
CONTROL_PLANE_IP=$(kubectl get nodes -l 'node-role.kubernetes.io/control-plane' -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
check_metadata() { kubectl -n "$1" exec "$2" -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/; }
kubectl get networkpolicy -A
check_metadata starfleet shuttle
check_metadata outpost drifter
check_metadata dock tender
kubectl -n outpost get deployment runtime-peek -o jsonpath='{.spec.template.spec.volumes[*].hostPath.path}{"\n"}'
```

The policy list is empty, the three requests print `200`, and the last command prints the socket path.

## Block the metadata address and the kubelet ports

Save this as `networkpolicy-block-node.yaml`. It has no namespace, so you apply it to each namespace with `-n`. Replace `<WORKER_IP>` and `<CONTROL_PLANE_IP>` with the stored addresses:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-metadata-and-node-ports
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 169.254.169.254/32
        - <WORKER_IP>/32
        - <CONTROL_PLANE_IP>/32
```

Apply it to the three namespaces:

```sh
for namespace in starfleet outpost dock; do
  kubectl apply -n "$namespace" -f networkpolicy-block-node.yaml
done
```

## Open the metadata address for the agent

Save this as `networkpolicy-allow-metadata-agent.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-metadata-agent
  namespace: starfleet
spec:
  podSelector:
    matchLabels:
      role: cloud-agent
  policyTypes:
  - Egress
  egress:
  - to:
    - ipBlock:
        cidr: 169.254.169.254/32
    ports:
    - protocol: TCP
      port: 80
```

Apply it:

```sh
kubectl apply -f networkpolicy-allow-metadata-agent.yaml
```

For `agent` the union of the two policies allows every address except the nodes, plus the metadata address. The kubelet ports stay closed for it.

## Remove the socket mount

The Deployment mounts the socket through a volume and a volume mount. Edit the Deployment and delete both:

```sh
kubectl -n outpost edit deployment runtime-peek
```

In the editor, remove the `volumeMounts` list from the container and the `volumes` list from the pod template, then save. The Deployment rolls out a new pod. Wait for it:

```sh
kubectl -n outpost rollout status deployment/runtime-peek
```

## Verify every path

Wait a few seconds, then check the denied and allowed paths. The denied requests print `000` with exit code 28, and the allowed requests print `200`, except the secure kubelet port, which would print `401` if it were reachable:

```sh
check_metadata starfleet agent
check_metadata starfleet shuttle
check_metadata outpost drifter
check_metadata dock tender
kubectl -n starfleet exec agent -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "http://$WORKER_IP:10255/pods"
kubectl -n dock exec tender -- curl -sk -m 3 -o /dev/null -w '%{http_code}\n' "https://$CONTROL_PLANE_IP:10250/pods"
kubectl -n outpost exec drifter -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe/
kubectl -n metadata-stub exec control -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "http://$WORKER_IP:10255/pods"
```

Only the first request prints `200` among the metadata checks. The two kubelet requests print `000`. The last two requests print `200`: the Service works and the control pod still reaches the read-only port, which proves the block comes from the policies and not from a failure of the node.

After recording your result, remove the independent lab with `astrona destroy ats-031-capstone-040`.

## Common pitfalls

> [!WARNING]
> - **Writing one policy for the metadata address and another for the node ports.** Together they allow both.
> - **Forgetting the control plane node address.** Its kubelet answers on port 10250.
> - **Editing the pod instead of the Deployment.** The volume list of a running pod cannot be changed.
> - **Leaving the mount in only one of the two places.** Remove both the volume and the volume mount.
