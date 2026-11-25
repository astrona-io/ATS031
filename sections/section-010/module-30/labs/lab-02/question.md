---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Repair A Two-Entry Peer Rule

Allow about 10 minutes for the tasks.

The `assay` pod should accept samples only from the `sampler` in `starfleet-031-010-03-02`. A review found that the `idler` in `starfleet-031-010-03-02` and the `sampler` next to the assay also get in.

## Connect to the lab

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-03-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-03-02" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

## Starting state

The namespace `dock-031-010-03-02` runs the pods `assay` and `sampler`. The namespace `starfleet-031-010-03-02` runs the pods `sampler` and `idler`, and the namespace `outpost-031-010-03-02` runs one more pod named `sampler`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. Each namespace has the automatic label `kubernetes.io/metadata.name: <namespace name>`.

The NetworkPolicy `assay-from-starfleet` in `dock-031-010-03-02` selects the `assay` pod. Its one ingress rule lists two peer entries: a `namespaceSelector` for `starfleet-031-010-03-02`, and a separate `podSelector` for `app: sampler`.

## Tasks

1. Find out why the `idler` pod in `starfleet-031-010-03-02` and the `sampler` pod in `dock-031-010-03-02` can reach the `assay` pod today.
2. Repair the NetworkPolicy `assay-from-starfleet` so that it admits TCP port 8080 only from pods with the label `app: sampler` in the namespace `starfleet-031-010-03-02`. Keep the policy name.
3. Do not add other policies, in `dock-031-010-03-02` or in any other namespace.

## Check your work

The test client prints `open` with the reply, or `blocked` when the connection times out:

```sh
ASSAY_IP=$(kubectl -n dock-031-010-03-02 get pod assay -o jsonpath='{.status.podIP}')
kubectl -n starfleet-031-010-03-02 exec sampler -- python /app/client.py tcp "$ASSAY_IP" 8080
kubectl -n starfleet-031-010-03-02 exec idler -- python /app/client.py tcp "$ASSAY_IP" 8080
kubectl -n dock-031-010-03-02 exec sampler -- python /app/client.py tcp "$ASSAY_IP" 8080
```

The first command must print `open`. The other two must print `blocked`.
