---
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

Traefik runs as the Deployment `traefik` in the namespace `ingress-system`, with the ServiceAccount `traefik` and the ClusterRole `traefik`. The IngressClass `traefik` names the controller `traefik.io/ingress-controller`. The namespace `starfleet-031-030-02-02` holds the Deployment and Service `cargo` and the Ingress `cargo` for `cargo.local` on the `web` entrypoint, with the class `traefik`. The installation has two mistakes.

Fix the argument of the Deployment `traefik` that selects the IngressClass, so Traefik watches the class `traefik`. Give the ClusterRole `traefik` the missing read access that Traefik needs to find the pod addresses behind a Service. The ClusterRole must keep only the verbs `get`, `list` and `watch`. Change only the other arguments if you must, and do not change the Ingress `cargo`. After the repair, a plain HTTP request with the host `cargo.local` must reach `cargo`.
