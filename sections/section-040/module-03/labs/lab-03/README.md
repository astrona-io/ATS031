# Remove A Runtime Socket Mount

Remove the `hostPath` mount of the containerd socket directory from a Deployment, make its container run as a user other than root, and keep its other volumes.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
