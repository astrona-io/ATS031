---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Restrict The etcd Data Directory

Find the etcd data directory from the running process, restrict its mode to 700, and record which user runs etcd.

The task and solution use a VM from the pinned `24.04-cks` image with a one-node kubeadm cluster (Kubernetes v1.35.10). `vm/` holds the scripts astrona pipes into the VM; regenerate them with `python3 scripts/ci/vm-lab.py <this folder>` after you change a lab file. Run `astrona test` on this folder: `vm/install.sh` builds the cluster and runs `bootstrap/setup.sh` in the VM, `testing/verify-start.sh` checks that every outcome fails on the starting state, then `solution/apply.sh` applies the reference solution and every outcome must pass.
