# Find Host-Network Pods And Block New Ones

List the pods that use the network namespace of the node, then make Pod Security admission reject new host-network pods in one namespace.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
