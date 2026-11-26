# Record A Test Matrix For A Policy Set — Solution

You solve this lab by testing seven rows and writing the results into one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Read the policies and write down what you expect for each row before you measure:

```sh
kubectl -n starfleet-031-010-04-04 get pods -o wide --show-labels
kubectl -n outpost-031-010-04-04 get pods -o wide --show-labels
kubectl -n starfleet-031-010-04-04 get networkpolicy -o yaml
kubectl -n outpost-031-010-04-04 get networkpolicy
```

`default-deny-all` isolates every pod in `starfleet-031-010-04-04` in both directions. `hangar-ingress` admits TCP port 8080 to `hangar` from `rover` or from any pod in `outpost-031-010-04-04`. `rover-egress` lets `rover` send to `hangar` on TCP port 8080 and to CoreDNS on port 53. Nothing allows `vault` to receive, and nothing allows `tanker` to send. No policy selects `drone`, so it may send anywhere.

A connection needs both sides: egress from the source and ingress to the target. From this reading, you expect `rover-to-hangar` and `drone-to-hangar` to be `open`, the other three traffic rows to be `blocked`, `rover-dns` to be `resolved` and `tanker-dns` to be `unresolved`.

## Step 2: measure every row (checks `starfleet-rows`, `outpost-rows` and `dns-rows`)

Every pod has a small test client. It prints `open`, `blocked`, `resolved` or `unresolved` as its first word. The helpers below take a namespace and a pod name, so each row is one short command that prints only that word:

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

Compare each word with your expectation. A row that differs is a finding to explain before anyone changes the policies, and you record the measured word, not the expected one.

## Step 3: record the rows from starfleet (check `starfleet-rows`)

The rows `rover-to-hangar`, `rover-to-vault` and `tanker-to-hangar` start in `starfleet-031-010-04-04`, so both the egress and the ingress policies of that namespace decide them.

## Step 4: record the rows from outpost (check `outpost-rows`)

The rows `drone-to-hangar` and `drone-to-vault` start in `outpost-031-010-04-04`, where no policy exists. Only the ingress side in `starfleet-031-010-04-04` decides them.

## Step 5: record the DNS rows and write the ConfigMap (checks `dns-rows`, `starfleet-rows` and `outpost-rows`)

The rows `rover-dns` and `tanker-dns` show whether a pod may send to CoreDNS on port 53. Only `rover-egress` allows that.

Write all seven rows into one ConfigMap. The values below are the words from Step 2 for this policy set; if a command printed a different word, write that word instead.

Save this as `configmap-test-matrix.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: test-matrix
  namespace: starfleet-031-010-04-04
data:
  rover-to-hangar: open
  rover-to-vault: blocked
  tanker-to-hangar: blocked
  drone-to-hangar: open
  drone-to-vault: blocked
  rover-dns: resolved
  tanker-dns: unresolved
```

Apply it:

```sh
kubectl apply -f configmap-test-matrix.yaml
```

Then read back what you recorded:

```sh
kubectl -n starfleet-031-010-04-04 get configmap test-matrix -o jsonpath='{.data}'
```

The output must show all seven keys, each with one word. The grader sends the same requests again and compares each answer with the recorded word.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not change, add or delete any NetworkPolicy in either namespace. The checks compare every policy with its starting spec and reject any policy in `outpost-031-010-04-04`.
>
> Write only `open` or `blocked` for traffic rows and only `resolved` or `unresolved` for DNS rows. A key name with a typo, a missing key or a full client line such as `open hangar port=8080` fails the check.
>
> Test pod addresses, not names. A failed DNS lookup and a blocked connection look the same when you test by name.
>
> A row that times out can also mean a broken pod. Keep one row that you expect to be open, so you know the client works.
