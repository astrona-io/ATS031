---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Record A Test Matrix For A Policy Set

Allow about 12 minutes for the tasks.

Before anyone changes the policy set in `starfleet`, the team wants a record of what it allows today. Write the expected result first, then measure.

## Connect to the lab

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-04-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-04-04" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

## Starting state

The namespace `starfleet-031-010-04-04` runs the pods `rover`, `tanker`, `hangar` and `vault`, and the namespace `outpost-031-010-04-04` runs the pod `drone`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. Three NetworkPolicies exist in `starfleet-031-010-04-04`: `default-deny-all`, `hangar-ingress` and `rover-egress`. There is no policy in `outpost-031-010-04-04`.

## Tasks

1. Read the three policies and write down what you expect for each row below.
2. Test every row with a bounded request. For traffic rows, send the request to the pod IP address of the target on TCP port 8080. For DNS rows, look up `kubernetes.default.svc.cluster.local`.
3. Record the measured result in a ConfigMap named `test-matrix` in `starfleet-031-010-04-04`, with one key per row. Use `open` or `blocked` for traffic rows and `resolved` or `unresolved` for DNS rows.
4. Do not change any policy.

| Key | Source | Test |
| --- | --- | --- |
| `rover-to-hangar` | `rover` in `starfleet-031-010-04-04` | `hangar`, TCP 8080 |
| `rover-to-vault` | `rover` in `starfleet-031-010-04-04` | `vault`, TCP 8080 |
| `tanker-to-hangar` | `tanker` in `starfleet-031-010-04-04` | `hangar`, TCP 8080 |
| `drone-to-hangar` | `drone` in `outpost-031-010-04-04` | `hangar`, TCP 8080 |
| `drone-to-vault` | `drone` in `outpost-031-010-04-04` | `vault`, TCP 8080 |
| `rover-dns` | `rover` in `starfleet-031-010-04-04` | DNS lookup |
| `tanker-dns` | `tanker` in `starfleet-031-010-04-04` | DNS lookup |

## Check your work

The test client prints `open`, `blocked`, `resolved` or `unresolved` as its first word. For example, for the first row:

```sh
HANGAR_IP=$(kubectl -n starfleet-031-010-04-04 get pod hangar -o jsonpath='{.status.podIP}')
kubectl -n starfleet-031-010-04-04 exec rover -- python /app/client.py tcp "$HANGAR_IP" 8080
```

Then read back what you recorded:

```sh
kubectl -n starfleet-031-010-04-04 get configmap test-matrix -o yaml
```

The ConfigMap must have all seven keys, each with the measured word.
