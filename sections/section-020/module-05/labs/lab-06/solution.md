---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Remove Write Access To The CoreDNS Configuration Solution

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The `test` line stops the shell when `kubectl` points at another cluster.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-05-06)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-05-06" || exit 1
```

Every step of this lab uses `kubectl` only. No step runs a command on a node.

## Confirm the problem

The `auth can-i` command asks the API server whether a user or service account may do an action. `--as` makes the request as that identity. Ask for the default service account of the `outpost-031-020-05-06` namespace:

```sh
kubectl auth can-i update configmap/coredns -n kube-system --as=system:serviceaccount:outpost-031-020-05-06:default
kubectl auth can-i patch configmap/coredns -n kube-system --as=system:serviceaccount:outpost-031-020-05-06:default
```

Both answers are `yes`. Any process in a pod of that namespace that uses the token of this service account can change the DNS answers of the whole cluster.

## Find the grant

A grant in one namespace comes from a RoleBinding there. List the RoleBindings in `kube-system` with their subjects, and look for the service account:

```sh
kubectl -n kube-system get rolebindings -o wide
```

The output has one binding whose `SERVICEACCOUNTS` column names `outpost-031-020-05-06/default`. Read the Role it points to:

```sh
kubectl -n kube-system describe rolebinding <BINDING>
kubectl -n kube-system describe role <ROLE>
```

The Role allows `update` and `patch` on all ConfigMaps in `kube-system`.

## Remove the grant

The binding and the Role exist only for this grant, so delete both. Then ask again:

```sh
kubectl -n kube-system delete rolebinding <BINDING>
kubectl -n kube-system delete role <ROLE>
kubectl auth can-i update configmap/coredns -n kube-system --as=system:serviceaccount:outpost-031-020-05-06:default
kubectl auth can-i patch configmap/coredns -n kube-system --as=system:serviceaccount:outpost-031-020-05-06:default
```

Both answers are now `no`.

## Tighten the pod records

With `pods insecure`, CoreDNS answers a pod name built from any IP address without checking that such a pod exists. With `pods verified`, it answers only for pods that exist. Save the current ConfigMap first, because the `reload` plugin applies a mistake to every CoreDNS pod:

```sh
kubectl -n kube-system get configmap coredns -o yaml > configmap-coredns-before.yaml
kubectl -n kube-system edit configmap coredns
```

In the editor, change the line `pods insecure` to `pods verified` and save. Then check the text and the name resolution:

```sh
kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}' | grep pods
kubectl -n starfleet-031-020-05-06 exec shuttle -- nslookup probe.starfleet-031-020-05-06.svc.cluster.local
```

The Corefile shows `pods verified`, and the `probe` Service still resolves to its cluster IP address. The `reload` plugin applies the new Corefile within about a minute without a restart.

## Common pitfalls

> [!WARNING]
> Deleting the `system:coredns` ClusterRoleBinding breaks DNS for the whole cluster; remove only the extra grant. `kubectl auth can-i` without `--as` checks your own administrator rights. A syntax error in the Corefile reaches every CoreDNS pod through the `reload` plugin; keep the saved copy.
