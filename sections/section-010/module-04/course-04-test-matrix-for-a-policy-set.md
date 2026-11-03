---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Test Matrix For A Policy Set

A policy set is correct when every path that should work does work, and every path that should fail does fail. Testing one request proves one cell of that table. This part builds the table for the `starfleet` application, runs it with bounded requests, and uses the result to see which paths of the broken set still fail.

## Write the expected table first

A test matrix lists each source, each destination, and the expected result. Write it before you test, so the test cannot change your expectation. The application has three needs and several paths that must stay closed:

| Source | Destination | Expected |
| --- | --- | --- |
| `scout` | DNS query to CoreDNS | works |
| `scout` | `probe` Service on port 80 | works |
| `scout` | Kubernetes API server | works |
| `drifter` in `outpost` | `probe` pods in `starfleet` | blocked |
| `drifter` in `outpost` | `scout` pod | blocked |

The `scout` script covers the first three rows. The last two need a request from the `drifter` pod to a pod address.

## Bounded requests with readable results

An unbounded request hangs the shell, and a bare `wget` failure says little. Wrap the request in a small shell function that sets a time limit and prints one word. Define it in your shell, then use it for every row. The function uses `wget -T 3`, so each request ends within about three seconds.

<!-- astrona:playground:renew -->

```sh
check_path() {
  namespace="$1"; pod="$2"; url="$3"
  if kubectl -n "$namespace" exec "$pod" -- wget -q -T 3 -O /dev/null "$url" 2>/dev/null; then
    echo "reachable: $pod -> $url"
  else
    echo "blocked:   $pod -> $url"
  fi
}
```

The function prints `reachable` when the request returns a successful status, and `blocked` for any failure. It cannot tell a timeout from a refusal. When a row needs that difference, run the plain `wget` command and read its message.

## Run the matrix

Collect the pod addresses of the destinations, then run the two rows for `drifter` and the script for `scout`:

```sh
PROBE_IP=$(kubectl -n starfleet get pod -l app=probe -o jsonpath='{.items[0].status.podIP}')
SCOUT_IP=$(kubectl -n starfleet get pod scout -o jsonpath='{.status.podIP}')
check_path outpost drifter "http://$PROBE_IP:8080/"
check_path outpost drifter "http://$SCOUT_IP:8080/"
kubectl -n starfleet exec scout -- python /app/check.py
```

The two `drifter` rows must show `blocked`. The `scout` line shows one result for each of `dns`, `probe` and `api`. A blocked row that should be reachable is a fault to repair. A reachable row that should be blocked is a leak and a more serious fault. The playground set has faults of the first kind, so the `probe` step of `scout` is expected to fail until the set is repaired.

## Why use addresses for the blocked rows

The `drifter` in `outpost` has no policy. DNS works for it, so it could use names. Pod addresses remove one variable: the request cannot fail because of name resolution, so a block is a policy block. For a client under an egress baseline, names fail for DNS reasons first, and an address shows whether the connection itself is allowed.

## Counters and evidence

NetworkPolicy has no counters. Plugins may offer them. In Calico, packet and drop counters and flow logs are plugin features, not part of the Kubernetes API, and they depend on how Calico is installed. In the exam and in this playground, the evidence is the request result. Record each row with its time, source, destination and result, so that a later change can be compared with the same table.

Run the matrix before and after every change. You now have a repeatable test, and the failing `probe` step shows that the set is still broken. The next part finds out why.

## Common pitfalls

> [!WARNING]
> - **Testing only the allowed rows.** Leaks show in the blocked rows.
> - **Running a request without a time limit.** A dropped packet then hangs the shell.
> - **Writing the expectation after the test.** The result then confirms itself.
> - **Treating a refusal as a block.** A refusal means a pod answered. Only a timeout shows a drop.
