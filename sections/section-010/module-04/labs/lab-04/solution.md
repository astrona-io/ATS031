---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Record A Test Matrix For A Policy Set Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-04-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-04-04" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

A test matrix lists each source, each target and the result you expect, and then records what really happens. Read the policies first and write down your expectation for each row:

```sh
kubectl -n starfleet-031-010-04-04 get networkpolicy -o yaml
```

`default-deny-all` isolates every pod in `starfleet-031-010-04-04` in both directions. `hangar-ingress` admits TCP port 8080 to `hangar` from `rover` or from any pod in `outpost-031-010-04-04`. `rover-egress` lets `rover` send to `hangar` on TCP port 8080 and to CoreDNS on port 53. Nothing allows `vault` to receive, and nothing allows `tanker` to send.

Now measure each row. The helpers below take a namespace and a pod name, so each row is one short command:

```sh
pod_address() { kubectl -n "$1" get pod "$2" -o jsonpath='{.status.podIP}'; }
check_path() { kubectl -n "$1" exec "$2" -- python /app/client.py tcp "$(pod_address "$3" "$4")" 8080 | cut -d' ' -f1; }
check_dns() { kubectl -n "$1" exec "$2" -- python /app/client.py dns kubernetes.default.svc.cluster.local | cut -d' ' -f1; }
check_path starfleet-031-010-04-04 rover starfleet-031-010-04-04 hangar
check_path starfleet-031-010-04-04 rover starfleet-031-010-04-04 vault
check_path starfleet-031-010-04-04 tanker starfleet-031-010-04-04 hangar
check_path outpost-031-010-04-04 drone starfleet-031-010-04-04 hangar
check_path outpost-031-010-04-04 drone starfleet-031-010-04-04 vault
check_dns starfleet-031-010-04-04 rover
check_dns starfleet-031-010-04-04 tanker
```

Each command prints one word. Compare it with your expectation; a row that differs is a finding to explain before anyone changes the policies. Then record the measured words in the ConfigMap. Replace each `<RESULT>` with the word that the matching command printed:

```sh
kubectl -n starfleet-031-010-04-04 create configmap test-matrix \
  --from-literal=rover-to-hangar=<RESULT> \
  --from-literal=rover-to-vault=<RESULT> \
  --from-literal=tanker-to-hangar=<RESULT> \
  --from-literal=drone-to-hangar=<RESULT> \
  --from-literal=drone-to-vault=<RESULT> \
  --from-literal=rover-dns=<RESULT> \
  --from-literal=tanker-dns=<RESULT>
```

Then check the result:

```sh
kubectl -n starfleet-031-010-04-04 get configmap test-matrix -o yaml
```

The grader sends the same requests again and compares each answer with the recorded word.

When you are done, remove the lab with `astrona destroy ats-031-lab-010-04-04`.

## Common pitfalls

> [!WARNING]
> Test pod addresses, not names. A failed DNS lookup and a blocked connection look the same when you test by name.
>
> A row that times out can also mean a broken pod. Keep one row that you expect to be open, so you know the client works.
