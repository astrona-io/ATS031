---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Block A Simulated Metadata Endpoint

Solve this question on: `terminal`

The namespace `starfleet-031-040-01-01` runs the `probe` Deployment (two pods labelled `app: probe`, port 8080) behind the Service `probe`, and the client pod `shuttle` labelled `app: shuttle`. The namespace `outpost-031-040-01-01` runs the client pod `drifter`. Calico, the network plugin of this cluster, enforces NetworkPolicy. No policy exists yet. You will add a pod that plays the part of a metadata endpoint, and keep `shuttle` away from it while it keeps its permitted dependencies. This models the network boundary only. It does not secure a real cloud provider metadata service, and it does not cover pods on the host network.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-01-01" || exit 1
node_name="astro-ats-031-lab-040-01-01-control-plane"
worker_name="astro-ats-031-lab-040-01-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

Allow about 8 minutes for task work. Cluster startup adds time.

## Tasks

1. Create the pod `metadata-simulator` in `starfleet-031-040-01-01` with the label `app: metadata-simulator` and `restartPolicy: Never`. Its one container is named `web`, uses the image `docker.io/library/python:3.13-alpine` and runs the command `python -m http.server 8080`.
2. Create the NetworkPolicy `shuttle-isolation` in `starfleet-031-040-01-01`. It selects the pods labelled `app: shuttle`, covers egress only, and allows two things: DNS to the CoreDNS pods (`k8s-app: kube-dns` in the namespace `kube-system`) on UDP and TCP port 53, and the pods labelled `app: probe` on TCP port 8080.
3. Prove the result. `shuttle` must still get a response with `version=v1` from `http://probe/`, and its request to the `metadata-simulator` pod address on port 8080 must time out. A request from `drifter` to the same address must still get the directory listing.

## Constraints

- Keep the `probe` Deployment, the `shuttle` pod and the `drifter` pod running and unchanged.
- Do not add a policy that blocks `drifter`.

## How the answer is checked

The grader runs two checks. The first reads the pod `metadata-simulator` and needs the label, container, image and command from the first task, with the pod running and ready, and a request from `drifter` to the pod address on port 8080 must return a page that contains `Directory listing`. The second reads the NetworkPolicy `shuttle-isolation`, which must have exactly the selector, policy type and two egress rules from the second task, and a request from `shuttle` to the `metadata-simulator` pod address on port 8080 must time out. Both checks also need the `probe` Deployment fully rolled out and a response with `version=v1` from `shuttle` to `http://probe/`.

Hint: Calico updates its rules a few seconds after you apply a policy. Repeat your test requests before you submit.
