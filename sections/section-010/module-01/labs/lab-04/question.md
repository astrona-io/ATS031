---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Find The Policy That Blocks A Request

Allow about 10 minutes for the tasks.

The `lander` pod in `outpost` must deliver to the `depot` pod on TCP port 8080, but every request times out. The team says the policies were written for exactly this path.

## Connect to the lab

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-01-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-01-04" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

## Starting state

The namespace `outpost-031-010-01-04` runs three pods: `lander`, `depot` and `stray`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. Three NetworkPolicies exist: `default-deny-all`, `lander-egress` and `depot-ingress`.

## Tasks

1. Find out which policy blocks the request from `lander` to `depot` on TCP port 8080, and why.
2. Repair that policy so the request succeeds. Keep the policy names.
3. Keep `default-deny-all` unchanged. Do not delete it or add allow rules to it.
4. Do not open any other path: `stray` must still time out to `depot`, and `lander` must still time out to `stray`.

## Check your work

The test client prints `open` with the reply, or `blocked` when the connection times out. Use pod IP addresses:

```sh
DEPOT_IP=$(kubectl -n outpost-031-010-01-04 get pod depot -o jsonpath='{.status.podIP}')
kubectl -n outpost-031-010-01-04 exec lander -- python /app/client.py tcp "$DEPOT_IP" 8080
kubectl -n outpost-031-010-01-04 exec stray -- python /app/client.py tcp "$DEPOT_IP" 8080
```

The first command must print `open` and the second `blocked`.
