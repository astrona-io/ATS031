---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Remediate Findings End To End

On the exam and in real work, a single fix is rarely the task. You get a list of failing checks on a node, and you must close each one without breaking the node, and you must show that they are closed. The method is always the same loop: audit, back up, change one setting, restart, audit again and compare. This part runs the loop for a mixed list of findings on the worker kubelet, and states what the evidence proves.

## The loop

1. Audit: record the state before any change.
2. Pick the findings that you can and must fix, and note those you do not fix with the reason.
3. Back up every file you touch, outside directories that a service loads.
4. Change one setting at a time and check the file.
5. Restart the component that reads the file and wait for it.
6. Audit again and compare with the first record.

Step 6 is the one people skip. A file edit is not a result. The result is the effective value on the running process, plus a working node.

## The audit with kube-bench

`kube-bench` runs the checks of the benchmark against a node. The target `node` covers the worker node section. The command below assumes that the binary and its `cfg` directory are staged in `/opt/training/kube-bench` on the worker. If the playground has no binary there, skip this step and use the manual audit in the next section. A `kind` node differs from a kubeadm virtual machine in file locations and service names, so `kube-bench` can report failures or warnings that come from the container layout, not from a weak setting. Read each failing check before you act on it.

<!-- astrona:playground:renew -->

```sh
WORKER=astro-ats-031-playground-020-05-worker
podman exec $WORKER sh -c 'cd /opt/training/kube-bench && ./kube-bench run --targets node' > kube-bench-before.txt
grep -e '^\[FAIL\]' kube-bench-before.txt
```

The `grep` lists the failing checks by number and text. Match each one to a setting that you know from this module. Keep the file as the record from before.

## A manual audit you can repeat

The function below prints the effective values that this module changed and the modes of the kubelet files. It reads `configz`, so it shows what the kubelet runs with. Save the output to a file before and after the change:

```sh
audit_kubelet() {
  kubectl get --raw "/api/v1/nodes/$WORKER/proxy/configz" | python3 -c 'import json,sys; c=json.load(sys.stdin)["kubeletconfig"]; print("anonymous", c["authentication"]["anonymous"]["enabled"]); print("authorization", c["authorization"]["mode"]); print("readOnlyPort", c.get("readOnlyPort", 0)); print("rotateCertificates", c.get("rotateCertificates")); print("streamingConnectionIdleTimeout", c.get("streamingConnectionIdleTimeout")); print("tlsMinVersion", c.get("tlsMinVersion"))'
  podman exec $WORKER stat -c '%a %n' /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
}
audit_kubelet > audit-before.txt
cat audit-before.txt
```

The output lists one line per setting. The playground starts with anonymous access on, the mode `AlwaysAllow`, the read-only port `10255`, rotation off and both files at mode `644`. If you applied some of these fixes in earlier steps, those lines already show the secure values. Read the real output of your cluster and do not assume it.

## Fix the list

Define a helper that sets one top-level key in the kubelet file. It removes the key if it exists and appends the new one, so the key appears only once. Then apply every setting that is still wrong. Each line is safe to run again, because the helper replaces the value:

```sh
set_kubelet_field() {
  podman exec $WORKER sed -i "/^$1:/d" /var/lib/kubelet/config.yaml
  podman exec $WORKER sh -c "printf '\n%s: %s\n' '$1' '$2' >> /var/lib/kubelet/config.yaml"
}
podman exec $WORKER cp /var/lib/kubelet/config.yaml /root/kubelet-config.yaml.bak
set_kubelet_field readOnlyPort 0
set_kubelet_field rotateCertificates true
set_kubelet_field streamingConnectionIdleTimeout 5m
set_kubelet_field tlsMinVersion VersionTLS12
podman exec $WORKER sed -i '/^  anonymous:/{n;s/enabled: true/enabled: false/}' /var/lib/kubelet/config.yaml
podman exec $WORKER sed -i 's/^  mode: AlwaysAllow$/  mode: Webhook/' /var/lib/kubelet/config.yaml
podman exec $WORKER chmod 600 /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
podman exec $WORKER grep -c -e '^readOnlyPort' -e '^rotateCertificates' -e '^streamingConnectionIdleTimeout' -e '^tlsMinVersion' /var/lib/kubelet/config.yaml
```

The last command counts the lines for the four keys. It must print `4`, one line per key. A larger number means a duplicate key, and the kubelet would not start. Do not restart until the count is right.

## Restart and compare

Restart the kubelet and wait for the API to answer through it. The loop reads `configz` until the anonymous setting is `False`, at most 30 times:

```sh
podman exec $WORKER systemctl restart kubelet
for attempt in $(seq 1 30); do
  if audit_kubelet 2>/dev/null | grep -q '^anonymous False'; then echo "kubelet restarted"; break; fi
  sleep 3
done
audit_kubelet > audit-after.txt
diff audit-before.txt audit-after.txt
kubectl get nodes
kubectl -n starfleet exec shuttle -- wget -q -T 3 -O- http://probe/
```

The `diff` shows each changed line, which is your evidence. Both nodes are `Ready`, and the `probe` Service still answers, so the node and the workload work. If you ran `kube-bench` before, run it again into `kube-bench-after.txt` and compare the lists of `[FAIL]` lines. The checks for the settings you fixed no longer appear there, and checks you did not touch remain. Some failures stay on a `kind` node because they come from the container layout, such as service file paths. Record them as not applicable with the reason.

## What the evidence proves

The comparison proves that the effective values changed and that the node and the application work. It does not prove that the cluster is compliant. The benchmark has many more checks. A passing tool result also depends on how the audit reads the node, and a check can pass while the setting is wrong or fail while the setting is right. This is why the loop ends with the effective value, not only with the tool output.

You have run the full loop once. On an exam the same loop applies with a different component each time: the API server manifest, the etcd manifest or the kubelet file.

## Common pitfalls

> [!WARNING]
> - **Skipping the first audit.** Without the before record you cannot show what changed.
> - **Fixing several files and restarting once without checking.** One duplicate key or typo stops the kubelet. Check the file first.
> - **Trusting the tool output alone.** Confirm the effective value on the running process.
> - **Counting a not applicable `kind` finding as a failure to fix.** Record it with the reason and move on.
