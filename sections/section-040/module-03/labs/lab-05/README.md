# Turn On NodeRestriction And Remove A Protected Node Label

Turn the `NodeRestriction` admission plugin back on in the kube-apiserver static pod, prove that the worker kubelet's own credential can no longer set protected labels on its own node, and remove the label it set.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
