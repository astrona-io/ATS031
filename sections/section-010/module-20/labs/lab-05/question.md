---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Apply One Baseline To Labelled Namespaces

Allow about 10 minutes for the tasks.

The fuel and cargo teams have agreed to a default-deny baseline. The galley team has not, and its namespace must stay open for now.

## Connect to the lab

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-02-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-02-05" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

## Starting state

Three namespaces exist: `cargo-031-010-02-05` runs the pod `loader`, `fuel-031-010-02-05` runs the pod `pump` and `galley-031-010-02-05` runs the pod `cook`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. No NetworkPolicy exists and no namespace carries a `netpol` label.

## Tasks

1. Add the label `netpol=restricted` to the namespaces `cargo-031-010-02-05` and `fuel-031-010-02-05`. Do not label `galley-031-010-02-05`.
2. Write one manifest for a NetworkPolicy named `default-deny-all` that selects every pod and isolates both ingress and egress. Leave the `namespace` field out of the manifest.
3. Apply that same file to every namespace that has the label `netpol=restricted`, selecting the namespaces by the label.
4. Do not create any policy in `galley-031-010-02-05`.

## Check your work

List the labelled namespaces and the policies, then send one request into a labelled namespace. The test client prints `open` with the reply, or `blocked` when the connection times out:

```sh
kubectl get namespaces -l netpol=restricted
kubectl get networkpolicy --all-namespaces
LOADER_IP=$(kubectl -n cargo-031-010-02-05 get pod loader -o jsonpath='{.status.podIP}')
kubectl -n galley-031-010-02-05 exec cook -- python /app/client.py tcp "$LOADER_IP" 8080
```

The request from `cook` must print `blocked`.
