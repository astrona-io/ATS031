---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Protect node metadata and endpoints

A workload reaches a node metadata service and obtains cloud authority that exceeds its own Kubernetes role. API least privilege did not protect this separate credential path.

The explanations identify the responsible components, compare intended and observed state, and work through the decisions needed to preserve the requirement. Read the worked examples as reasoning about a proposed system; no environment is started by this section.

Read the module goals, teaching and closing summary in order. YAML checks are indexed separately and appear after designated summaries. Larger domains include an intermediate checkpoint before the final review.

## Learning Outcomes

- Identify credentials and authority exposed through node-local endpoints.
- Separate workload network paths from host and control-plane paths.
- Explain cloud metadata protections and their implementation limits.
- Evaluate endpoint authentication, authorization and least privilege together.
