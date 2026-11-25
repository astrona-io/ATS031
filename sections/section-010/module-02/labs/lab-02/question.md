---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Deny All Ingress In One Namespace

Allow about 8 minutes for the tasks.

Nothing may open a connection to a pod in the `dock` namespace until the team writes allow rules. The pods in `dock` must still be able to call out.

## Connect to the lab

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-02-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-02-02" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

## Starting state

The namespace `dock-031-010-02-02` runs the pods `vault` and `crane`, and the namespace `outpost-031-010-02-02` runs the pod `visitor`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. No NetworkPolicy exists.

## Tasks

1. In the namespace `dock-031-010-02-02`, create a NetworkPolicy named `default-deny-ingress` that selects every pod in the namespace.
2. Make it isolate the pods for ingress only and allow no ingress.
3. Do not isolate the pods for egress, and do not create policies in `outpost-031-010-02-02`.

## Check your work

The test client prints `open` with the reply, or `blocked` when the connection times out:

```sh
VAULT_IP=$(kubectl -n dock-031-010-02-02 get pod vault -o jsonpath='{.status.podIP}')
VISITOR_IP=$(kubectl -n outpost-031-010-02-02 get pod visitor -o jsonpath='{.status.podIP}')
kubectl -n outpost-031-010-02-02 exec visitor -- python /app/client.py tcp "$VAULT_IP" 8080
kubectl -n dock-031-010-02-02 exec crane -- python /app/client.py tcp "$VAULT_IP" 8080
kubectl -n dock-031-010-02-02 exec crane -- python /app/client.py tcp "$VISITOR_IP" 8080
```

The first two commands must print `blocked`, also the one from the same namespace. The last one must print `open`.
