---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow DNS And One Application Dependency

Allow about 12 minutes for the tasks.

The `scanner` pod should talk to the `archive` and to nothing else. It finds the archive by name, so it also needs DNS.

## Connect to the lab

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-01-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-01-02" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

## Starting state

The namespace `starfleet-031-010-01-02` runs the Deployment `archive` with two replicas and the Service `archive`, plus the pods `scanner`, `decoy` and `idler`. The Service listens on port 80 and sends requests to the container port named `http`, which is TCP port 8080. The `decoy` pod is a healthy listener on TCP port 8080 with the label `app: decoy`; it is there to prove that unlisted egress is blocked. Each pod has the label `app: <name>` and contains a small test client, `/app/client.py`. No NetworkPolicy exists. CoreDNS, the cluster DNS server, runs in `kube-system` in pods with the label `k8s-app: kube-dns`.

## Tasks

1. In `starfleet-031-010-01-02`, create a NetworkPolicy named `scanner-egress` that selects only the pod with the label `app: scanner` and covers egress.
2. Allow DNS on UDP port 53 and TCP port 53 to the CoreDNS pods in `kube-system`. Select the namespace by its name label and the pods by `k8s-app: kube-dns` in one peer entry.
3. Allow TCP port 8080 to the pods with the label `app: archive` in the same namespace.
4. Allow nothing else. `scanner` must time out to `decoy`, and `decoy` must stay running and reachable for other pods.

## Check your work

The test client prints `open` with the reply, `blocked` when the connection times out, and `resolved` or `unresolved` for a DNS lookup:

```sh
kubectl -n starfleet-031-010-01-02 exec scanner -- python /app/client.py dns archive.starfleet-031-010-01-02.svc.cluster.local
ARCHIVE_SERVICE_IP=$(kubectl -n starfleet-031-010-01-02 get service archive -o jsonpath='{.spec.clusterIP}')
DECOY_IP=$(kubectl -n starfleet-031-010-01-02 get pod decoy -o jsonpath='{.status.podIP}')
kubectl -n starfleet-031-010-01-02 exec scanner -- python /app/client.py tcp "$ARCHIVE_SERVICE_IP" 80
kubectl -n starfleet-031-010-01-02 exec scanner -- python /app/client.py tcp "$DECOY_IP" 8080
```

The lookup must print `resolved` and the Service address. The request to the archive must print `open` and the request to the decoy must print `blocked`.
