# Hardening The API Server Playground

Author README for the ungraded playground. The guide is in `docs/overview.md`.

The playground runs one QEMU VM from the `24.04-cks` image of
[qcow2-base-image](https://github.com/astrona-io/qcow2-base-image). The image
ships a held kubeadm v1.35 node, containerd 2.2.1, the kube-bench v0.10.6
binary (config in `/etc/kube-bench/cfg`) and image, and
`/usr/local/sbin/astrona-kubeadm-init`. `bootstrap/setup.sh` runs inside the
VM as the `astrona` user: it creates the single-node cluster
`astro-ats-031-playground-020-03` (control plane without taint), gives the
`astrona` and `student` users a kubeconfig, and applies the start objects
(`starfleet` with `probe` and `shuttle`, `outpost` with `drifter`), which are
inlined because astrona copies no other files into the VM. It then copies the
static pod manifests to `/opt/training/backup`, writes the audit policy to
`/opt/training/audit-policy.yaml` and sets mode `644` on the API server,
controller manager and scheduler manifests. The learner logs in as `student`
with `astrona ssh astro-ats-031-playground-020-03`.

`validate.sh` only checks that the seed objects and the API server are ready.
It does not grade anything; the playground has no solution or testing files.
Live run on 2026-11-18 (arm64): every command and output in the guide and in
the module parts was seen on that run. The audit logging edit was made with a
script instead of an interactive editor. API server restarts took 42 seconds
(audit logging) and 46 seconds (`--profiling=false`); the mirror pod stayed
`0/1` for up to about 50 seconds after the wait loop ended.
