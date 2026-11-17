---
exam_objectives:
- Protect node metadata and endpoints
---
# Starting Environment

The cluster has one control plane node and one worker node. The kubelet on the worker reads its settings from the file `/var/lib/kubelet/config.yaml`, and that file sets `readOnlyPort: 10255`. The read-only port answers HTTP requests without any credential. The namespace `dock-031-040-03-01` has a pod `inspector` with the `curl` command. No NetworkPolicy exists.
