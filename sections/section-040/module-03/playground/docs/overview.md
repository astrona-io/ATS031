---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Guided Practice: Protect Node Endpoints

Use a host shell with the private kubeconfig for this module playground. A kubeconfig identifies the cluster and credentials that `kubectl`, the Kubernetes command-line tool, uses.

<!-- astrona:playground:renew -->

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-playground-040-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-playground-040-03" || exit 1
```

## What is running

The cluster has one control plane node and one worker node. The kubelet on the worker serves its read-only port 10255 on purpose, and both kubelets serve HTTPS on port 10250. The namespaces `starfleet`, `outpost` and `dock` each have a `probe` Deployment and Service on port 80 and a client pod with the `curl` command. The namespace `metadata-stub` has a pod `control` that no policy selects. The pods `runtime-peek`, `cri-helper`, `log-reader` and `net-tool` expose host resources. No NetworkPolicy exists. The fake metadata server from the metadata exercises is also in place.

Store the address of the worker node and look at the kubelet ports from a client pod:

```sh
WORKER_IP=$(kubectl get nodes -l '!node-role.kubernetes.io/control-plane' -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
kubectl -n starfleet exec shuttle -- curl -sk -m 3 -o /dev/null -w '%{http_code}\n' "https://$WORKER_IP:10250/pods"
kubectl -n starfleet exec shuttle -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' "http://$WORKER_IP:10255/pods"
```

The first request prints `401` and the second prints `200`.

## Try it

Write a NetworkPolicy for `dock` that selects all pods and allows `0.0.0.0/0` except the addresses of the nodes. Apply it and repeat the two requests from `tender`. Then list every pod that has a host path or uses the host network, and read the `NodeRestriction` setting from the API server pod.
