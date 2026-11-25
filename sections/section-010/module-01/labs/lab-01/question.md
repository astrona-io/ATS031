---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow One Peer And Deny Another

Allow about 10 minutes for the tasks.

Only the `tender` pod may send requests to the `hub` pods. The `idler` next to it and the `stranger` in `outpost` must lose access, but nothing else may change for them.

## Connect to the lab

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-01-01" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

## Starting state

The namespace `starfleet-031-010-01-01` runs the Deployment `hub` with two replicas and the Service `hub`, plus the pods `tender`, `idler` and `mirror`. The Service listens on port 80 and sends requests to the container port named `http`, which is TCP port 8080. The namespace `outpost-031-010-01-01` runs the pod `stranger`. Each pod has the label `app: <name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. No NetworkPolicy exists.

## Tasks

1. In `starfleet-031-010-01-01`, create a NetworkPolicy named `hub-from-tender` that selects the `hub` pods and covers ingress only.
2. Allow ingress on TCP port 8080 only from pods with the label `app: tender` in the same namespace.
3. Do not create any other policy, in `starfleet-031-010-01-01` or in `outpost-031-010-01-01`. The `idler` and `stranger` pods must still reach the `mirror` pod.

## Check your work

The test client prints `open` with the reply, or `blocked` when the connection times out:

```sh
HUB_SERVICE_IP=$(kubectl -n starfleet-031-010-01-01 get service hub -o jsonpath='{.spec.clusterIP}')
kubectl -n starfleet-031-010-01-01 exec tender -- python /app/client.py tcp "$HUB_SERVICE_IP" 80
kubectl -n starfleet-031-010-01-01 exec idler -- python /app/client.py tcp "$HUB_SERVICE_IP" 80
kubectl -n outpost-031-010-01-01 exec stranger -- python /app/client.py tcp "$HUB_SERVICE_IP" 80
```

The first command must print `open`. The other two must print `blocked`.
