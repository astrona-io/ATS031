# Block Pod Access To The Kubelet Ports

Both kubelets serve HTTPS on port 10250, and the kubelet on the worker also serves its read-only port 10255. The pods in `outpost-031-040-03-02` do not need the kubelet. Create one NetworkPolicy in `outpost-031-040-03-02` that applies to every pod in the namespace, while DNS and Services keep working.

1. Pod `drifter` can no longer reach port 10250 on the worker or on the control plane node.
2. `drifter` can no longer reach port 10255 on the worker.
3. A new pod in `outpost-031-040-03-02`, whatever its labels, is blocked from both kubelet ports and still reaches `http://probe/` and `http://probe.starfleet-031-040-03-02.svc.cluster.local/`.

`drifter` must keep reaching both `probe` Services, and nothing changes in the other namespaces: `shuttle` in `starfleet-031-040-03-02` must still reach the read-only port.
