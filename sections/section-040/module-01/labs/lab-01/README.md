# Bring A Host-Network Workload Back Under NetworkPolicy

The namespace has an egress allow-list for every pod, but the `relay` Deployment runs with `hostNetwork: true`, so the policy does not select it and it still reaches a metadata-style endpoint. The learner moves the workload back to the pod network, so the existing policy applies to it.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
