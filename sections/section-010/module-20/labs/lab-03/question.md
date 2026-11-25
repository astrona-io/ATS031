---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Deny All Egress And Observe DNS Fail

Allow about 8 minutes for the tasks.

The pods in the `dock` namespace must not open any outgoing connection until the team has listed what they need. Other pods must still be able to call them.

## Connect to the lab

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-02-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-02-03" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

## Starting state

The namespace `dock-031-010-02-03` runs the pods `hauler` and `winch`, and the namespace `outpost-031-010-02-03` runs the pod `pilot`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. No NetworkPolicy exists.

## Tasks

1. In the namespace `dock-031-010-02-03`, create a NetworkPolicy named `default-deny-egress` that selects every pod in the namespace.
2. Make it isolate the pods for egress only and allow no egress.
3. Do not isolate the pods for ingress, and do not create policies in `outpost-031-010-02-03`.

## Check your work

The test client prints `open` with the reply, `blocked` when the connection times out, and `resolved` or `unresolved` for a DNS lookup:

```sh
PILOT_IP=$(kubectl -n outpost-031-010-02-03 get pod pilot -o jsonpath='{.status.podIP}')
HAULER_IP=$(kubectl -n dock-031-010-02-03 get pod hauler -o jsonpath='{.status.podIP}')
kubectl -n dock-031-010-02-03 exec hauler -- python /app/client.py tcp "$PILOT_IP" 8080
kubectl -n dock-031-010-02-03 exec winch -- python /app/client.py dns kubernetes.default.svc.cluster.local
kubectl -n outpost-031-010-02-03 exec pilot -- python /app/client.py tcp "$HAULER_IP" 8080
```

The first command must print `blocked` and the second `unresolved`. The last one must print `open`, because the reply to an allowed incoming connection is not new egress.
