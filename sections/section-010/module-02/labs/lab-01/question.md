---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Apply A Default-Deny Baseline And Allow One Path

Allow about 12 minutes for the tasks.

The `outpost-031-010-02-01` namespace must start from "nothing is allowed". After that, only the `smith` pod may send requests to the `forge` pod.

## Connect to the lab

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-02-01" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

## Starting state

The namespace `outpost-031-010-02-01` runs the pods `forge`, `smith` and `idler`, and the namespace `dock-031-010-02-01` runs the pod `visitor`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. No NetworkPolicy exists, so every pod can reach every other pod.

## Tasks

1. In `outpost-031-010-02-01`, create a NetworkPolicy named `default-deny-all` that selects every pod and isolates it for both ingress and egress, with no rules.
2. Add one policy that lets the `forge` pod accept TCP port 8080 only from the `smith` pod.
3. Add one policy that lets the `smith` pod send to the `forge` pod on TCP port 8080 only.
4. Do not open anything else. The `idler` pod must stay fully isolated, and the `visitor` pod in `dock-031-010-02-01` must time out to `forge`.

## Check your work

The test client prints `open` with the reply, `blocked` when the connection times out, and `resolved` or `unresolved` for a DNS lookup:

```sh
FORGE_IP=$(kubectl -n outpost-031-010-02-01 get pod forge -o jsonpath='{.status.podIP}')
kubectl -n outpost-031-010-02-01 exec smith -- python /app/client.py tcp "$FORGE_IP" 8080
kubectl -n dock-031-010-02-01 exec visitor -- python /app/client.py tcp "$FORGE_IP" 8080
kubectl -n outpost-031-010-02-01 exec idler -- python /app/client.py dns kubernetes.default.svc.cluster.local
```

The first command must print `open`, the second `blocked` and the third `unresolved`.
