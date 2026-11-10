# Block Pod Access To The Kubelet Ports

Stop the pods of one namespace from reaching the kubelet ports on the nodes while DNS and Services keep working.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
