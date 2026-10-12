---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify platform binaries before deploying

A verified download and the binary actually executed have different hashes. Verification described one artifact, while installation selected another. The trust decision must stay linked to execution.

The explanations identify the responsible components, compare intended and observed state, and work through the decisions needed to preserve the requirement. Read the worked examples as reasoning about a proposed system; no environment is started by this section.

Read the module goals, teaching and closing summary in order. YAML checks are indexed separately and appear after designated summaries. Larger domains include an intermediate checkpoint before the final review.

## Learning Outcomes

- Distinguish integrity checks from publisher authenticity.
- Bind verification evidence to an exact release and architecture.
- Explain authenticated checksum and signature trust chains.
- Preserve verified bytes through storage and deployment.
