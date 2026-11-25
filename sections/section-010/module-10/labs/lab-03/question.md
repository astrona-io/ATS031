---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Isolate One Pod For Egress Only

Allow about 10 minutes for the tasks.

The `relay` pod in `starfleet` must stop opening connections of its own. Other pods must still be able to send requests to it.

## Connect to the lab

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-01-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-01-03" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

## Starting state

The namespace `starfleet-031-010-01-03` runs three pods: `relay`, `lander` and `courier`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. No NetworkPolicy exists, so every pod can reach every other pod.

## Tasks

1. In the namespace `starfleet-031-010-01-03`, create a NetworkPolicy named `relay-egress-isolation` that selects only the pod with the label `app: relay`.
2. Make the policy isolate `relay` for egress (outgoing traffic) and allow no egress at all. DNS lookups from `relay` stop too.
3. Do not isolate `relay` for ingress (incoming traffic): `courier` must still reach `relay` on TCP port 8080. Set `policyTypes` explicitly so this is clear.
4. Do not change the `lander` and `courier` pods, and do not create other policies in the namespace.

## Check your work

The test client prints one word for each attempt: `open` with the reply, `blocked` when the connection times out, `refused` when nothing listens, or `resolved` and `unresolved` for a DNS lookup. Use pod IP addresses, so DNS and traffic are tested separately:

```sh
LANDER_IP=$(kubectl -n starfleet-031-010-01-03 get pod lander -o jsonpath='{.status.podIP}')
RELAY_IP=$(kubectl -n starfleet-031-010-01-03 get pod relay -o jsonpath='{.status.podIP}')
kubectl -n starfleet-031-010-01-03 exec relay -- python /app/client.py tcp "$LANDER_IP" 8080
kubectl -n starfleet-031-010-01-03 exec relay -- python /app/client.py dns kubernetes.default.svc.cluster.local
kubectl -n starfleet-031-010-01-03 exec courier -- python /app/client.py tcp "$RELAY_IP" 8080
```

The first two commands must print `blocked` and `unresolved`. The last command must still print `open`.
