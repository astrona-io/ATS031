# Close The Kubelet Read-Only Port

The kubelet on the worker node `astro-ats-031-lab-040-03-01-worker` serves its read-only port 10255, which sends the pod list to any caller without a credential. Pod `inspector` in `dock-031-040-03-01` can read it from the worker address.

1. Set `readOnlyPort` in `/var/lib/kubelet/config.yaml` on the worker to `0`, or remove the line.
2. Make the running kubelet use the new value, so its configuration from the API server shows no read-only port.
3. Port 10255 on the worker no longer answers.

The worker must stay `Ready`, and the kubelet HTTPS port 10250 must keep serving and keep refusing anonymous requests.
