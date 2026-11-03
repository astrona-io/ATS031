---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Block Pod Access To The Kubelet Ports Solution

## Inspect the starting state

Read the addresses of the nodes. They are the addresses you must exclude:

```sh
kubectl get nodes -o wide
WORKER_IP=$(kubectl get nodes -l '!node-role.kubernetes.io/control-plane' -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
CONTROL_PLANE_IP=$(kubectl get nodes -l 'node-role.kubernetes.io/control-plane' -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
kubectl -n outpost exec drifter -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "http://$WORKER_IP:10255/pods"
kubectl -n outpost exec drifter -- curl -sk -m 3 -o /dev/null -w '%{http_code}\n' "https://$WORKER_IP:10250/pods"
```

The first request prints `200` because the read-only port answers without a credential. The second prints `401`, because the secure port refuses an unauthenticated request. Both prove that the ports are reachable.

## Create the policy

The policy selects all pods and allows `0.0.0.0/0` except the address of each node. Replace `<WORKER_IP>` and `<CONTROL_PLANE_IP>` with the two addresses you stored.

Save this as `networkpolicy-block-node-ports.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-node-ports
  namespace: outpost
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

## Verify

Wait a few seconds, then check the blocked ports, the Services and the controls:

```sh
kubectl -n outpost exec drifter -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "http://$WORKER_IP:10255/pods"
kubectl -n outpost exec drifter -- curl -sk -m 3 -o /dev/null -w '%{http_code}\n' "https://$WORKER_IP:10250/pods"
kubectl -n outpost exec drifter -- curl -sk -m 3 -o /dev/null -w '%{http_code}\n' "https://$CONTROL_PLANE_IP:10250/pods"
kubectl -n outpost exec drifter -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe/
kubectl -n outpost exec drifter -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://probe.starfleet.svc.cluster.local/
kubectl -n starfleet exec shuttle -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "http://$WORKER_IP:10255/pods"
```

The first three requests print `000` with exit code 28. The last three print `200`. An alternative that also passes the check is a policy that allows all addresses on the port ranges 1 to 10249, 10251 to 10254 and 10256 to 65535, with `endPort`.
After recording your result, remove the independent lab with `astrona destroy ats-031-lab-040-03-01`.
