---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow A TCP Port Range And A Named UDP Port

Allow about 12 minutes for the tasks.

The `surveyor` in `outpost` reads `meter` data on three TCP ports and a UDP port. The `admin` port of `meter` must stay closed to it, and the `loiterer` gets nothing.

## Connect to the lab

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-03-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-03-05" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

## Starting state

The namespace `starfleet-031-010-03-05` runs the pod `meter`. It listens on TCP ports 7000, 7001, 7002 and 7100, and on UDP port 7200. Its pod spec names TCP port 7100 `admin` and UDP port 7200 `tick`. The namespace `outpost-031-010-03-05` runs the pods `surveyor` and `loiterer`. Each pod has the label `app: <pod name>` and contains a small test client, `/app/client.py`. No NetworkPolicy exists.

## Tasks

1. In `starfleet-031-010-03-05`, create a NetworkPolicy named `meter-ports` that selects the pod with the label `app: meter`.
2. Allow ingress only from the `surveyor` pod in `outpost-031-010-03-05`. Use one peer entry that selects the namespace by its name label and the pod by its label.
3. Allow TCP ports 7000 to 7002 with a single port item that uses `endPort`.
4. Allow UDP by the container port name `tick`, not by its number.
5. Do not allow TCP port 7100.

## Check your work

The test client prints `open` with the reply, `blocked` when no reply comes within three seconds, or `refused` when the port is open but nothing listens. Add `udp` instead of `tcp` for the UDP test:

```sh
METER_IP=$(kubectl -n starfleet-031-010-03-05 get pod meter -o jsonpath='{.status.podIP}')
kubectl -n outpost-031-010-03-05 exec surveyor -- python /app/client.py tcp "$METER_IP" 7002
kubectl -n outpost-031-010-03-05 exec surveyor -- python /app/client.py udp "$METER_IP" 7200
kubectl -n outpost-031-010-03-05 exec surveyor -- python /app/client.py tcp "$METER_IP" 7100
```

The first two commands must print `open`. The last one must print `blocked`.
