# Close Metadata Gaps Across Namespaces

The metadata address is blocked in some namespaces and not in others. One policy selects a single pod, one namespace has no policy, and the one complete block also stops a pod that needs the address. The learner tests coverage from new pods, closes the gaps and adds a label-based exception.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
