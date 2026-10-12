---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Properly set up Ingress with TLS

A client requests `probe.local`, and Traefik chooses an Ingress route before forwarding to the `probe` Service. The Ingress object declares matching rules; the controller implements them. A rule stored without an active controller cannot provide the same routing behavior.

The explanations identify the responsible components, compare intended and observed state, and work through the decisions needed to preserve the requirement. Read the worked examples as reasoning about a proposed system; no environment is started by this section.

Read the module goals, teaching and closing summary in order. YAML checks are indexed separately and appear after designated summaries. Larger domains include an intermediate checkpoint before the final review.

## Learning Outcomes

- Identify IngressClass and controller responsibility.
- Compare exact, prefix and implementation-specific paths.
- Trace host and Service port matching.
- Explain TLS termination and backend protocol limits.
- Explain public keys, private keys and certificate authority trust.
- Distinguish server authentication from mutual TLS.
- Relate identity names, validity and trust chains to verification.
- Describe rotation and compromise recovery for certificate-based identities.
