---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow One Pod From Another Namespace

Allow about 10 minutes for the tasks.

Only the `courier` in `outpost-031-010-03-01` may deliver to the `registry`. The couriers in other namespaces carry the same label and must not get in.

## Connect to the lab

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-03-01" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

## Starting state

The namespace `starfleet-031-010-03-01` runs the pods `registry` and `courier`. The namespace `outpost-031-010-03-01` runs the pods `courier` and `idler`, and the namespace `dock-031-010-03-01` runs one more pod named `courier`. Each pod has the label `app: <pod name>`, so three pods carry `app: courier`. Each pod serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. Each namespace has the automatic label `kubernetes.io/metadata.name: <namespace name>`. No NetworkPolicy exists.

## Tasks

1. In `starfleet-031-010-03-01`, create a NetworkPolicy named `registry-from-outpost-courier` that selects the `registry` pod and covers ingress.
2. Admit TCP port 8080 only from pods with the label `app: courier` in the namespace `outpost-031-010-03-01`. Use one peer entry that has both a `namespaceSelector` and a `podSelector`.
3. Do not create policies in any other namespace, and do not add a second policy in `starfleet-031-010-03-01`.

## Check your work

The test client prints `open` with the reply, or `blocked` when the connection times out:

```sh
REGISTRY_IP=$(kubectl -n starfleet-031-010-03-01 get pod registry -o jsonpath='{.status.podIP}')
kubectl -n outpost-031-010-03-01 exec courier -- python /app/client.py tcp "$REGISTRY_IP" 8080
kubectl -n dock-031-010-03-01 exec courier -- python /app/client.py tcp "$REGISTRY_IP" 8080
kubectl -n starfleet-031-010-03-01 exec courier -- python /app/client.py tcp "$REGISTRY_IP" 8080
```

The first command must print `open`. The other two must print `blocked`.
