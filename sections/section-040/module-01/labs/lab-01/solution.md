---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Block A Simulated Metadata Endpoint Solution

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-01-01" || exit 1
node_name="astro-ats-031-lab-040-01-01-control-plane"
worker_name="astro-ats-031-lab-040-01-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Inspect And Explain

The isolated environment has two healthy probe replicas, an internal Service and two client Pods. The required result has not been configured.

Inspect the current objects before changing them:

```sh
kubectl -n starfleet get pods -o wide
kubectl get nodes -o wide
```

Create metadata-simulator as a healthy Python HTTP server with label app metadata-simulator on port 8080. Configure shuttle-isolation to allow only DNS and probe application traffic. A direct metadata-simulator request from shuttle must time out while an unrestricted drifter request proves that listener works. This models the network boundary; it does not claim to secure a cloud provider metadata service or host-network bypass.

Save this as `pod-metadata-simulator.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: metadata-simulator
  namespace: starfleet
  labels:
    app: metadata-simulator
spec:
  restartPolicy: Never
  containers:
  - name: web
    image: docker.io/library/python:3.13-alpine
    command:
    - python
    - -m
    - http.server
    - '8080'
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: shuttle-isolation
  namespace: starfleet
spec:
  podSelector:
    matchLabels:
      app: shuttle
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - port: 53
      protocol: UDP
    - port: 53
      protocol: TCP
  - to:
    - podSelector:
        matchLabels:
          app: probe
    ports:
    - port: 8080
      protocol: TCP
```

Apply the scoped correction:

```sh
kubectl apply -f pod-metadata-simulator.yaml
```

## Verify The Result

Observe the actual result. A denied request returns a nonzero status when the denial works, so run it separately from a shell sequence that stops on error. Status convergence and a successful request establish different parts of the result.

```sh
kubectl -n starfleet wait --for=condition=Ready pod/metadata-simulator --timeout=180s
kubectl -n starfleet exec shuttle -- wget -q -T 3 -O- http://probe/
```

Separate permitted application dependencies from a metadata-style endpoint in the private network. The commands above deliberately target one environment. Keep its remaining components available so an unrelated failure cannot stand in for the required denial or correction. No example command output is presented as evidence of a completed run. A matching field alone does not establish that a process used it or that a controller reconciled it.

After recording your result, remove the independent lab with `astrona destroy ats-031-lab-040-01-01`.

## Common pitfalls

> [!WARNING]
> Confirm the private context and exact node names before a change. Check the stated scope and live result. Do not change unrelated components to hide the original fault.
