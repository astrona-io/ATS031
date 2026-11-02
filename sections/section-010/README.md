---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Use Network security policies to restrict cluster level access

A pod holds a database password and a stranger pod from another namespace can still open a connection to it. Kubernetes allows all pod traffic until a NetworkPolicy selects a pod, and the rules that follow are additive and easy to widen by mistake. This section teaches how isolation is decided, how to write ingress and egress policies, and how to prove with real requests that the right peer gets in and the wrong one does not.

## Learning Path

1. Restrict Pod Traffic With NetworkPolicy: the landing page and the playground.
2. How NetworkPolicy Isolation Works
3. Allow One Peer With An Ingress Policy
4. Restrict Egress And Allow DNS
5. Default Deny And Troubleshooting Policies
6. Summary, then the ten-question knowledge check.

The parts carry the hands-on steps. Each lab follows the part that practises its skill. The playground is a private `kind` cluster with Kubernetes v1.35; launch it from the landing page and keep it running while you read.

## Learning Outcomes

- Explain which pods a policy isolates, in which direction, and how several policies combine.
- Write an ingress policy that allows one labelled peer and denies all others, including a peer in another namespace.
- Write an egress policy that allows DNS and one application dependency and blocks everything else.
- Explain why `namespaceSelector` and `podSelector` in one peer entry differ from two separate peer entries.
- Test a policy with an allowed request and a denied request, and tell a timeout from a refused connection.
