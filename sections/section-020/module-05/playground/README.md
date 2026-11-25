# Kubelet And CoreDNS Review Playground

Author README for the ungraded playground. The guide is in `docs/overview.md`.

The playground runs one QEMU VM from the `24.04-cks` image of
[qcow2-base-image](https://github.com/astrona-io/qcow2-base-image). The image
ships a held kubeadm v1.35 node, the kube-bench v0.10.6 binary and
`/usr/local/sbin/astrona-kubeadm-init`. `bootstrap/setup.sh` runs inside the
VM as the `astrona` user: it creates the single-node cluster
`astro-ats-031-playground-020-05`, gives the `astrona` and `student` users a
kubeconfig, and applies the start objects, which are inlined because astrona
copies no other files into the VM. It then copies the kubelet configuration to
`/opt/training/backup/kubelet-config.yaml` and opens the kubelet: anonymous
authentication on, `AlwaysAllow`, `readOnlyPort: 10255`,
`rotateCertificates: false`, `streamingConnectionIdleTimeout: 0s`, no
`tlsMinVersion`, and mode 644 on `config.yaml` and `kubelet.conf`. The learner
logs in as `student` with `astrona ssh astro-ats-031-playground-020-05`.

`validate.sh` only checks that the seed objects are ready. It does not grade
anything. Live run on 2026-11-18 (arm64): every command and output in the
guide and in the module parts was seen on that run.
