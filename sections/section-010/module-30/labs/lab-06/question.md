---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Repair A Policy That Names The Service Port And Add A Port Range

Allow about 12 minutes for the tasks.

The `visitor` should reach the `kiosk` Service, but every request times out. The new `collector` also needs the three metrics ports of every `kiosk` replica.

## Connect to the lab

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-03-06)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-03-06" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

## Starting state

The namespace `starfleet-031-010-03-06` runs the Deployment `kiosk` with two replicas, the Service `kiosk` and the pods `visitor` and `collector`. The Service listens on port 80 and sends requests to the container port named `http`, which is TCP port 8080. The `kiosk` pods also serve metrics on TCP ports 9100, 9101 and 9102. Each pod has the label `app: <name>` and contains a small test client, `/app/client.py`. Two NetworkPolicies exist: `default-deny-ingress` and `kiosk-ingress`.

## Tasks

1. Find out why `visitor` cannot reach the Service `kiosk` on port 80, and repair the policy `kiosk-ingress`.
2. In the same policy, add a rule that lets the `collector` pod reach TCP ports 9100 to 9102 on the `kiosk` pods. Use one port item with `endPort`.
3. Keep `default-deny-ingress` as it is. `visitor` must not reach the metrics ports, and `collector` must not reach port 8080.

## Check your work

The test client prints `open` with the reply, or `blocked` when the connection times out. Test the Service and one pod address directly:

```sh
KIOSK_SERVICE_IP=$(kubectl -n starfleet-031-010-03-06 get service kiosk -o jsonpath='{.spec.clusterIP}')
KIOSK_POD_IP=$(kubectl -n starfleet-031-010-03-06 get pods -l app=kiosk -o jsonpath='{.items[0].status.podIP}')
kubectl -n starfleet-031-010-03-06 exec visitor -- python /app/client.py tcp "$KIOSK_SERVICE_IP" 80
kubectl -n starfleet-031-010-03-06 exec collector -- python /app/client.py tcp "$KIOSK_POD_IP" 9101
kubectl -n starfleet-031-010-03-06 exec visitor -- python /app/client.py tcp "$KIOSK_POD_IP" 9101
```

The first two commands must print `open` and the last one must print `blocked`. Repeat the pod test with `{.items[1].status.podIP}` for the second replica.
