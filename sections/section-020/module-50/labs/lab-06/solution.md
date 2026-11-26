# Remove Write Access To The CoreDNS Configuration — Solution

You solve this lab by deleting one RoleBinding and its Role, and by changing one line of the Corefile. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The `auth can-i` command asks the API server whether a user or service account may do an action. `--as` makes the request as that identity. Ask for the default service account of the `outpost-031-020-05-06` namespace:

```sh
kubectl auth can-i update configmap/coredns -n kube-system --as=system:serviceaccount:outpost-031-020-05-06:default
kubectl auth can-i patch configmap/coredns -n kube-system --as=system:serviceaccount:outpost-031-020-05-06:default
```

Both answers are `yes`. Any process in a pod of that namespace that uses the token of this service account can change the DNS answers of the whole cluster.

## Step 2: remove the grant (check `coredns-write-access`)

A grant in one namespace comes from a RoleBinding there. List the RoleBindings in `kube-system` with their subjects, and look for the service account:

```sh
kubectl -n kube-system get rolebindings -o wide
```

One binding, `dns-maintenance`, names `outpost-031-020-05-06/default` in its `SERVICEACCOUNTS` column. Read the binding and the Role it points to:

```sh
kubectl -n kube-system describe rolebinding dns-maintenance
kubectl -n kube-system describe role dns-maintenance
```

The Role allows `get`, `update` and `patch` on all ConfigMaps in `kube-system`. The binding and the Role exist only for this grant, so delete both:

```sh
kubectl -n kube-system delete rolebinding dns-maintenance
kubectl -n kube-system delete role dns-maintenance
```

## Step 3: keep the CoreDNS permissions (check `coredns-rbac-kept`)

CoreDNS reads Services, endpoints, pods and namespaces through the `coredns` service account in `kube-system`. That access comes from the ClusterRoleBinding `system:coredns`, not from the grant you removed. Check that it is still there and still works:

```sh
kubectl get clusterrolebinding system:coredns -o wide
kubectl auth can-i watch endpointslices.discovery.k8s.io --as=system:serviceaccount:kube-system:coredns
```

The binding points to the ClusterRole `system:coredns` and names `kube-system/coredns`, and the answer is `yes`. Change nothing here.

## Step 4: tighten the pod records (check `pod-records`)

With `pods insecure`, CoreDNS answers a pod name built from any IP address without checking that such a pod exists. With `pods verified`, it answers only for pods that exist. Save the current ConfigMap first, because the `reload` plugin applies a mistake to every CoreDNS pod:

```sh
kubectl -n kube-system get configmap coredns -o yaml > configmap-coredns-before.yaml
kubectl -n kube-system edit configmap coredns
```

In the editor, inside the block of the `kubernetes` plugin, change the line `pods insecure` to `pods verified` and save. Leave every other line as it is.

The `reload` plugin applies the new Corefile within about a minute, without a restart.

## Step 5: test the result

Ask again as the service account, then check the Corefile text and the name resolution:

```sh
kubectl auth can-i update configmap/coredns -n kube-system --as=system:serviceaccount:outpost-031-020-05-06:default
kubectl auth can-i patch configmap/coredns -n kube-system --as=system:serviceaccount:outpost-031-020-05-06:default
kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}' | grep pods
kubectl -n starfleet-031-020-05-06 exec shuttle -- nslookup probe.starfleet-031-020-05-06.svc.cluster.local
```

Both `auth can-i` answers are now `no`. The Corefile shows `pods verified`, and the `probe` Service still resolves to its cluster IP address.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Deleting the `system:coredns` ClusterRoleBinding or editing the `system:coredns` ClusterRole breaks DNS for the whole cluster and fails `coredns-rbac-kept`. Remove only the extra grant.
>
> `kubectl auth can-i` without `--as` checks your own administrator rights, not the rights of the service account.
>
> A commented-out `pods insecure` line is fine, but the Corefile must hold an active `pods verified` or `pods disabled` line. A syntax error in the Corefile reaches every CoreDNS pod through the `reload` plugin and stops name resolution; keep the saved copy.
