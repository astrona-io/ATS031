---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Use Network security policies to restrict cluster level access

A pod holds a database password and a stranger pod from another namespace can still open a connection to it. Kubernetes allows all pod traffic until a NetworkPolicy selects a pod, and the rules that follow are additive and easy to widen by mistake. This section teaches how isolation is decided, how to write ingress and egress policies, and how to prove with real requests that the right peer gets in and the wrong one does not.

## Learning Path

1. Restrict Pod Traffic With NetworkPolicy: isolation, ingress, egress with DNS, default deny and troubleshooting.
2. Build Default-Deny Baselines For Namespaces: ingress and egress baselines, their side effects, and rolling them out to many namespaces.
3. Select Peers And Ports Precisely: namespace and pod selectors, one entry versus two, `ipBlock` with `except`, ports, protocols, `endPort` and Services.
4. Policy For Real Cluster Traffic And Troubleshooting: DNS, the API server, probes, `hostNetwork` pods, a test matrix and an audit method.
5. Capstone: secure three namespaces with a complete policy set.

Each module ends with a summary and a ten-question knowledge check. The parts carry the hands-on steps. Each lab follows the part that practises its skill. The playground is a private `kind` cluster with Kubernetes v1.35; launch it from the landing page and keep it running while you read.

## Learning Outcomes

- Explain which pods a policy isolates, in which direction, and how several policies combine.
- Write an ingress policy that allows one labelled peer and denies all others, including a peer in another namespace.
- Write an egress policy that allows DNS and one application dependency and blocks everything else.
- Explain why `namespaceSelector` and `podSelector` in one peer entry differ from two separate peer entries.
- Test a policy with an allowed request and a denied request, and tell a timeout from a refused connection.
