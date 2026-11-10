---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

The application and client fixtures are healthy. Complete the required change without replacing unrelated resources.

Create NetworkPolicy `probe-shuttle` selecting `app: probe` for ingress. Allow only same-namespace Pods labelled `app: shuttle` on TCP port 8080. Keep the original workload and clients healthy. Shuttle must receive version one through the Service; drifter in `outpost-031-010-01-01` must time out. Do not create any policy that also allows drifter.
