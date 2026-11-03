---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Guided Practice: Block The Metadata Address

Use a host shell with the private kubeconfig for this module playground. A kubeconfig identifies the cluster and credentials that `kubectl`, the Kubernetes command-line tool, uses.

<!-- astrona:playground:renew -->

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-playground-040-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-playground-040-02" || exit 1
```

## What is running

The cluster has the namespaces `starfleet`, `outpost` and `dock`, each with a `probe` Deployment and Service on port 80 and a client pod with the `curl` command. The pod `agent` in `starfleet` has the label `role=cloud-agent`. The namespace `metadata-stub` has the pod `fake-imds`, a fake metadata server on the host network of the worker node at `169.254.169.254` port 80, and a pod `control` that no policy selects. No NetworkPolicy exists.

Define a function and look at the baseline from the client pods:

```sh
check_metadata() { kubectl -n "$1" exec "$2" -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/; }
check_metadata starfleet shuttle
check_metadata outpost drifter
```

Both print `200`.

## Try it

Write a NetworkPolicy for `outpost` that selects all pods and allows `0.0.0.0/0` except `169.254.169.254/32`. Apply it and run the two checks again. The request from `drifter` must print `000`, and the request from `shuttle` must still print `200`. Then label a pod with `role=cloud-agent`, add a second policy that allows only the metadata address for that label, and watch the path open and close as you add and remove the label.
