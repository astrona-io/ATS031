# Restore API Server Authorization And Remove Anonymous Access — Solution

You solve this lab with one flag change in the API server manifest and one deleted RBAC binding. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Start with the request that the test made. `curl -k` skips the check of the server certificate, and without a client certificate or token the API server treats the request as the user `system:anonymous`:

```sh
sudo curl -sk -o /dev/null -w '%{http_code}\n' https://127.0.0.1:6443/api/v1/namespaces/starfleet-031-020-03-04/pods
sudo ps -eo args | grep '^kube-apiserver' | tr ' ' '\n' | grep -e '--authorization-mode' -e '--anonymous-auth'
```

The API server returns `200`, so the anonymous request can list pods. Two parts decide this: the authentication step accepts the anonymous user, and the authorization step allows the request. The second command shows `--authorization-mode=AlwaysAllow`. This authorizer allows every request, so RBAC rules are never checked.

## Step 2: restore the authorizers (check `authorization-mode`)

The kubelet watches `/etc/kubernetes/manifests` and starts every file in it as a static pod. Edit a copy in a work directory outside that folder, check the copy, and move it back in one step, so that the kubelet never reads a half-written file:

```sh
sudo mkdir -p /etc/kubernetes/edit
sudo cp -p /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/edit/kube-apiserver.yaml
sudo sed -i 's|--authorization-mode=AlwaysAllow|--authorization-mode=Node,RBAC|' /etc/kubernetes/edit/kube-apiserver.yaml
sudo grep -e '--authorization-mode' /etc/kubernetes/edit/kube-apiserver.yaml
sudo mv /etc/kubernetes/edit/kube-apiserver.yaml /etc/kubernetes/manifests/kube-apiserver.yaml
```

The API server restarts, so `kubectl` fails for a while. Wait until it answers again:

```sh
for attempt in $(seq 1 60); do
  if sudo ps -eo args | grep '^kube-apiserver ' | grep -q -e '--authorization-mode=Node,RBAC' && kubectl --request-timeout=3s get --raw=/readyz >/dev/null 2>&1; then echo "new flag visible and API server ready"; break; fi
  sleep 3
done
```

The old API server process can still answer for a few seconds after the `mv`, so the loop waits until the running process has the new flag and the API server is ready. It prints `new flag visible and API server ready`. If it ends without that message, run `sudo crictl ps -a --name kube-apiserver` and read the logs of the exited container with `sudo crictl logs <CONTAINER_ID>`.

## Step 3: remove the anonymous binding (check `anonymous-binding-removed`)

RBAC is now checked, but an RBAC binding can still allow the read. Find every ClusterRoleBinding with the subject `system:anonymous`:

```sh
kubectl get clusterrolebindings -o wide | grep -e NAME -e 'system:anonymous'
```

One binding gives the `view` ClusterRole to `system:anonymous`. Delete it, using the name from the output:

```sh
kubectl delete clusterrolebinding <BINDING_NAME>
```

## Step 4: test the anonymous request (check `anonymous-denied`)

```sh
sudo curl -sk -o /dev/null -w '%{http_code}\n' https://127.0.0.1:6443/api/v1/namespaces/starfleet-031-020-03-04/pods
sudo curl -sk https://127.0.0.1:6443/readyz
```

The pod list now returns `403`, and `/readyz` still prints `ok`. Anonymous authentication stays on, but RBAC allows the anonymous user only the health and version paths.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> The grader needs exactly `Node,RBAC`. `--authorization-mode` is a list: a second flag or an extra entry such as `AlwaysAllow` fails the check.
>
> Setting `--anonymous-auth=false` on a kubeadm API server also blocks the anonymous `/readyz` probe, so the check `anonymous-denied` fails and the API server pod is restarted again and again.
>
> Any ClusterRoleBinding with the subject `system:anonymous` fails the check, whatever its name or role.
