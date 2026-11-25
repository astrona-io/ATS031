---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Repair A Broken Policy Set

Allow about 15 minutes for the tasks.

After a change to the policies, the `pathfinder` pod cannot resolve names and cannot reach the `datastore`. Find each fault and repair it without opening anything extra.

## Connect to the lab

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-04-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-04-01" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

## Starting state

The namespace `starfleet-031-010-04-01` runs the pods `pathfinder`, `datastore` and `stranger`. The `pathfinder` pod uses the ServiceAccount `pathfinder`. Each pod has the label `app: <pod name>` and contains a small test client, `/app/client.py`. The `datastore` pod listens on TCP port 6379, and the other two pods serve HTTP on TCP port 8080.

Three NetworkPolicies exist. `default-deny-all` isolates every pod for both directions and is correct. `pathfinder-egress` is meant to let `pathfinder` use DNS, the `datastore` and the Kubernetes API server. `datastore-ingress` is meant to let only `pathfinder` connect to the `datastore`.

## Tasks

1. Test the three dependencies of the `pathfinder` pod: DNS, the `datastore` on TCP port 6379, and the API server through the `kubernetes` Service on port 443.
2. Repair `pathfinder-egress` so that DNS works on UDP port 53 and TCP port 53 to the CoreDNS pods (`k8s-app: kube-dns` in `kube-system`). Keep the `datastore` rule and the API server rule as they are.
3. Repair `datastore-ingress` so that it isolates the `datastore` pod for ingress and admits TCP port 6379 only from the `pathfinder` pod.
4. Keep `default-deny-all` unchanged. The `stranger` pod must time out to the `datastore`, and `pathfinder` must time out to `stranger`.

## Check your work

The test client prints `open` with the reply, `blocked` when the connection times out, and `resolved` or `unresolved` for a DNS lookup:

```sh
DATASTORE_IP=$(kubectl -n starfleet-031-010-04-01 get pod datastore -o jsonpath='{.status.podIP}')
API_SERVICE_IP=$(kubectl -n default get service kubernetes -o jsonpath='{.spec.clusterIP}')
kubectl -n starfleet-031-010-04-01 exec pathfinder -- python /app/client.py dns kubernetes.default.svc.cluster.local
kubectl -n starfleet-031-010-04-01 exec pathfinder -- python /app/client.py tcp "$DATASTORE_IP" 6379
kubectl -n starfleet-031-010-04-01 exec pathfinder -- python /app/client.py tcp "$API_SERVICE_IP" 443
kubectl -n starfleet-031-010-04-01 exec stranger -- python /app/client.py tcp "$DATASTORE_IP" 6379
```

The lookup must print `resolved`. The next two commands must print `open`, and the last one `blocked`.
