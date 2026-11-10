---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Block A Simulated Metadata Endpoint

Separate permitted application dependencies from a metadata-style endpoint in the private network.

The task and solution use a separate pinned kind cluster. Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
