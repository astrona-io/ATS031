---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

The application and client fixtures are healthy. Complete the required change without replacing unrelated resources.

Create `shuttle-egress` selecting `app: shuttle`. Allow DNS on TCP and UDP port 53 only to kube-system Pods labelled `k8s-app: kube-dns`, and allow TCP 8080 only to same-namespace Pods labelled `app: probe`. Keep a healthy `blocked-server` Pod with a different label. Shuttle must resolve and reach probe, while a direct request to the running blocked server must time out.
