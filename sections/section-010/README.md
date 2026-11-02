---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Use Network security policies to restrict cluster level access

A rule should allow only Pods labelled `app: shuttle` inside a selected namespace. Placing both selectors in one peer requires both matches. Splitting them into separate peers changes the condition into alternatives and can widen access.

The explanations identify the responsible components, compare intended and observed state, and work through the decisions needed to preserve the requirement. Read the worked examples as reasoning about a proposed system; no environment is started by this section.

Read the module goals, teaching and closing summary in order. YAML checks are indexed separately and appear after designated summaries. Larger domains include an intermediate checkpoint before the final review.

## Learning Outcomes

- Explain Pod selection and direction-specific network isolation.
- Evaluate additive allowed rules and selector structure.
- Relate DNS and dependencies to egress requirements.
- Distinguish declared policy from actual implementation enforcement.
