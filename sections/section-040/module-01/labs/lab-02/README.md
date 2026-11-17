# Restrict A Pod To An Egress Allow-List

The pod `courier` needs DNS and the `probe` Service and nothing else. The learner writes an egress allow-list NetworkPolicy for it, so that a metadata-style endpoint and every other destination are blocked. The grader proves the block with an unrestricted control pod and proves the allow-list with a destination that the policy does not name.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
