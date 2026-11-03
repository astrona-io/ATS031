# Block Pod Access To The Kubelet Ports

Stop the pods of one namespace from reaching the kubelet ports on the nodes while DNS and Services keep working.

Run `testing/smoke.sh` with the private kubeconfig of `ats-031-lab-040-03-01` to verify that the starting state fails grading and that the reference result passes. Static validation is not live evidence. Runtime verification has not been recorded yet.
