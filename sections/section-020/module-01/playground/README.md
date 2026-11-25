# Reviewing A Cluster Against A Security Benchmark Playground

Author README for the ungraded playground. The guide is in `docs/overview.md`.

The playground runs one QEMU VM from the `24.04-cks` image of
[qcow2-base-image](https://github.com/astrona-io/qcow2-base-image). The image
ships a held kubeadm v1.35 node, containerd 2.2.1, the kube-bench v0.10.6
binary (config in `/etc/kube-bench/cfg`) and image, and
`/usr/local/sbin/astrona-kubeadm-init`. `bootstrap/setup.sh` runs inside the
VM as the `astrona` user: it creates the single-node cluster
`astro-ats-031-playground-020-01` (control plane without taint), gives the
`astrona` and `student` users a kubeconfig, and applies the start objects
(`starfleet` with `probe` and `shuttle`, `outpost` with `drifter`), which are
inlined because astrona copies no other files into the VM. The learner logs in
as `student` with `astrona ssh astro-ats-031-playground-020-01`.

`validate.sh` only checks that the seed objects and the API server are ready.
It does not grade anything; the playground has no solution or testing files.
Live run on 2026-11-18 (arm64): every command and output in the guide and in
the module parts was seen on that run, including the API server restart after
the `--profiling=false` edit (40 to 70 seconds; kube-bench can still see the old
process for a few seconds after the wait loop ends).
