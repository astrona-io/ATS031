---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow API Server Egress For One Pod

Allow about 10 minutes for the tasks.

The `operator` pod watches the cluster and must talk to the Kubernetes API server again. The `helper` pod has no reason to reach the API server.

## Connect to the lab

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-04-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-04-03" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

## Starting state

The namespace `starfleet-031-010-04-03` runs the pods `operator` and `helper`. The `operator` pod uses the ServiceAccount `operator`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. Two NetworkPolicies exist: `default-deny-all` isolates every pod for both directions, and `allow-dns` lets every pod reach CoreDNS on port 53.

## Tasks

1. Find the address and port that the `kubernetes` Service in the `default` namespace sends requests to.
2. In `starfleet-031-010-04-03`, create a NetworkPolicy named `operator-to-api-server` that selects only the pod with the label `app: operator`.
3. Allow egress to that one address with an `ipBlock` that ends in `/32`, on that one TCP port.
4. Keep `default-deny-all` and `allow-dns` unchanged. The `helper` pod must still time out to the API server.

## Check your work

The test client prints `open` with the last reply line, or `blocked` when the connection times out. Test the Service address, as a real client does:

```sh
API_SERVICE_IP=$(kubectl -n default get service kubernetes -o jsonpath='{.spec.clusterIP}')
kubectl -n starfleet-031-010-04-03 exec operator -- python /app/client.py tcp "$API_SERVICE_IP" 443
kubectl -n starfleet-031-010-04-03 exec helper -- python /app/client.py tcp "$API_SERVICE_IP" 443
```

The first command must print `open` and the second `blocked`.
