---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Admit A Group Of Namespaces By Label

Allow about 10 minutes for the tasks.

Only the science division may read the `archive`. The survey and salvage teams belong to it, and new science namespaces will join later, so the rule must not list namespace names.

## Connect to the lab

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-03-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-03-03" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

## Starting state

The namespace `starfleet-031-010-03-03` runs the pod `archive`. The namespaces `survey-031-010-03-03`, `salvage-031-010-03-03` and `outpost-031-010-03-03` each run a pod named `mapper`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. No NetworkPolicy exists.

## Tasks

1. Add the label `division=science` to the namespaces `survey-031-010-03-03` and `salvage-031-010-03-03`. Do not label `outpost-031-010-03-03`.
2. In `starfleet-031-010-03-03`, create a NetworkPolicy named `archive-from-science` that selects the pod with the label `app: archive`.
3. Allow ingress to `archive` on TCP port 8080 from every pod in a namespace with the label `division=science`. Select the namespaces by that label, not by their names.
4. The `mapper` pod in `outpost-031-010-03-03` must time out.

## Check your work

The test client prints `open` with the reply, or `blocked` when the connection times out:

```sh
ARCHIVE_IP=$(kubectl -n starfleet-031-010-03-03 get pod archive -o jsonpath='{.status.podIP}')
kubectl get namespaces -l division=science
kubectl -n survey-031-010-03-03 exec mapper -- python /app/client.py tcp "$ARCHIVE_IP" 8080
kubectl -n outpost-031-010-03-03 exec mapper -- python /app/client.py tcp "$ARCHIVE_IP" 8080
```

The request from `survey-031-010-03-03` must print `open` and the request from `outpost-031-010-03-03` must print `blocked`.
