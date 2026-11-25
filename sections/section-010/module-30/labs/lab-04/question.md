---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow A Pod Range With ipBlock And except

Allow about 10 minutes for the tasks.

The `rogue` pod in `outpost` must lose access to the `ledger` at once. Its labels cannot be trusted, so the rule must use its address. Every other pod in the cluster keeps access.

## Connect to the lab

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-03-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-03-04" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

## Starting state

The namespace `starfleet-031-010-03-04` runs the pod `ledger`, which serves HTTP on TCP port 7070. The namespace `outpost-031-010-03-04` runs the pods `courier` and `rogue`, which serve HTTP on TCP port 8080. Each pod has the label `app: <pod name>` and contains a small test client, `/app/client.py`. No NetworkPolicy exists. The cluster gives pod addresses from the range `192.168.0.0/16`.

## Tasks

1. In `starfleet-031-010-03-04`, create a NetworkPolicy named `ledger-from-pod-range` that selects the pod with the label `app: ledger`.
2. Allow ingress on TCP port 7070 from an `ipBlock` for the pod range `192.168.0.0/16`.
3. Add an `except` entry that removes exactly the current address of the `rogue` pod (a `/32` entry).
4. Use no other peer form, and allow no other port.

## Check your work

The test client prints `open` with the reply, or `blocked` when the connection times out:

```sh
LEDGER_IP=$(kubectl -n starfleet-031-010-03-04 get pod ledger -o jsonpath='{.status.podIP}')
kubectl -n outpost-031-010-03-04 exec courier -- python /app/client.py tcp "$LEDGER_IP" 7070
kubectl -n outpost-031-010-03-04 exec rogue -- python /app/client.py tcp "$LEDGER_IP" 7070
```

The request from `courier` must print `open` and the request from `rogue` must print `blocked`.
