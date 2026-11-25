---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-05-02` is the control plane and also runs the pods. The `starfleet-031-020-05-02` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. A copy of the original kubelet configuration is in `/opt/training/backup/kubelet-config.yaml` on the node. The review lists these findings for the node `astro-ats-031-lab-020-05-02`:

1. `/var/lib/kubelet/config.yaml` has mode `644`.
2. `/etc/kubernetes/kubelet.conf` has mode `644`.
3. `rotateCertificates` is `false`.
4. `streamingConnectionIdleTimeout` has no useful value.
5. `tlsMinVersion` is not set.

Fix five kubelet findings on the node in one planned change: two file modes, certificate rotation, the streaming idle timeout and the minimum TLS version.
