# Pick The Release Files For A Node — Solution

You solve this lab by reading three values and recording them in one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The node of a `kind` cluster is a container on your machine. Open a shell on the control plane node (write `docker` instead of `podman` if your machine uses Docker):

```sh
podman exec -it astro-ats-031-lab-050-02-01-control-plane bash
```

List the release directory of the mirror:

```sh
ls /var/lib/k8s-mirror/release
```

It shows four version directories (`v1.33.7`, `v1.34.3`, `v1.35.1` and `v1.36.0-alpha.2`) and the text files `latest.txt`, `stable.txt`, `stable-1.33.txt`, `stable-1.34.txt` and `stable-1.35.txt`.

## Step 2: find the stable version (check `stable-version`)

The release site has no `latest` directory. The file `release/stable.txt` holds the version of the current stable release:

```sh
cat /var/lib/k8s-mirror/release/stable.txt; echo
```

`latest.txt` names the newest build, which is the pre-release `v1.36.0-alpha.2`. Each `stable-1.<minor>.txt` names the newest patch of one minor version. Neither is the current stable release, so use the version in `stable.txt`.

## Step 3: find the architecture of the worker (check `release-path`)

Leave the node shell with `exit`. The Kubernetes API reports the architecture of every node in the node status, already in the form that the release paths use:

```sh
kubectl get node astro-ats-031-lab-050-02-01-worker -o jsonpath='{.status.nodeInfo.architecture}{"\n"}'
```

It prints `amd64` or `arm64`. `uname -m` on the worker node would print `x86_64` for `amd64` and `aarch64` for `arm64`, which is not the form of the release paths.

## Step 4: read the published digest (check `release-digest`)

Put the version from Step 2 and the architecture from Step 3 into the path, and read the `.sha256` file next to `kubeadm`. Replace `<VERSION>` and `<ARCHITECTURE>`:

```sh
podman exec astro-ats-031-lab-050-02-01-control-plane cat /var/lib/k8s-mirror/release/<VERSION>/bin/linux/<ARCHITECTURE>/kubeadm.sha256; echo
```

The `.sha256` file holds only the 64-character digest, with no file name.

## Step 5: record the result (checks `stable-version`, `release-path` and `release-digest`)

Replace `<VERSION>`, `<ARCHITECTURE>` and `<DIGEST>` with your values. Save this as `configmap-release-pick.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: release-pick
  namespace: starfleet-031-050-02-01
data:
  path: "release/<VERSION>/bin/linux/<ARCHITECTURE>/kubeadm"
  sha256: "<DIGEST>"
```

Apply it:

```sh
kubectl apply -f configmap-release-pick.yaml
```

## Step 6: test the record

Print both keys:

```sh
kubectl -n starfleet-031-050-02-01 get configmap release-pick -o jsonpath='{.data.path}{"\n"}{.data.sha256}{"\n"}'
```

The first line must show the path with the version from `stable.txt` and the worker architecture. The second line must show the digest from Step 4.

## Step 7: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not use the version from `latest.txt` or from a `stable-1.<minor>.txt` file. Only `stable.txt` names the current stable release.
>
> Do not write `x86_64` or `aarch64` in the path. The release paths use `amd64` and `arm64`.
>
> Write the path relative to the mirror, starting with `release/`. The grader also accepts a leading `/var/lib/k8s-mirror/`, but no other prefix.
>
> Do not compute the digest of the `kubeadm` file yourself. The task asks for the published digest in `kubeadm.sha256`.
