# Close The Kubelet Read-Only Port

Turn off the read-only port 10255 of the kubelet on the worker node, restart the kubelet and keep the secure port 10250 working.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
