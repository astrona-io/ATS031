# Playground ats-031-playground-020-04

Author README for the ungraded playground. The guide is in `docs/overview.md`.

The playground runs one QEMU VM from the `24.04-cks` image of
[qcow2-base-image](https://github.com/astrona-io/qcow2-base-image). The image
ships a held kubeadm v1.35 node (containerd 2.2.1), the kube-bench v0.10.6
binary and `/usr/local/sbin/astrona-kubeadm-init`. It has no `etcdctl` binary;
the guide and the module parts run `etcdctl` (v3.6.6) inside the etcd pod.
`bootstrap/setup.sh` runs inside the VM as the `astrona` user: it creates the
single-node cluster `astro-ats-031-playground-020-04`, gives the `astrona` and
`student` users a kubeconfig, applies the start objects (inlined, because
astrona copies no other files into the VM), copies the API server and etcd
manifests and the kubelet configuration to `/opt/training/backup`, and sets
`/var/lib/etcd` to mode `755` as the finding. The learner logs in as `student`
with `astrona ssh astro-ats-031-playground-020-04`.

The configuration has no submission or grading fields. Live run on 2026-11-18
(arm64): every command and output in the guide and in the module parts was
seen on that run. The encryption at rest restart of the API server took about
45 seconds. kube-bench check 1.1.12 (etcd data directory owned by `etcd:etcd`)
fails on this node because kubeadm runs etcd as `root` and there is no `etcd`
user.
