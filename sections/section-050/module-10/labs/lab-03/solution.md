# Install A Verified Binary Into A Protected Directory — Solution

You solve this lab with a few commands on the node and one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The node of a `kind` cluster is a container on your machine. Open a shell on the control plane node (write `docker` instead of `podman` if your machine uses Docker):

```sh
podman exec -it astro-ats-031-lab-050-01-03-control-plane bash
```

Look at the owner and the mode of the install directory and the installed file:

```sh
stat -c '%a %U:%G %n' /opt/fleet /opt/fleet/bin /opt/fleet/bin/fleet-agent
```

The mode is `775` for `/opt/fleet` and `777` for `/opt/fleet/bin` and its `fleet-agent`. All three belong to user ID `1000`, not to `root`. Any user on the node can replace the file that will run.

## Step 2: close the install directories (check `protected-directories`)

Take the directories back first, so nobody else can swap the file after you install it. `chown` gives them to `root`, and mode `0755` lets only the owner write:

```sh
chown root:root /opt/fleet /opt/fleet/bin
chmod 0755 /opt/fleet /opt/fleet/bin
```

## Step 3: install the verified copy (check `installed-binary`)

Verify the signature before you use any digest from the manifest. `openssl dgst -sha256 -verify` prints `Verified OK` when the publisher's private key signed exactly this manifest:

```sh
cd /var/lib/fleet-release
openssl dgst -sha256 -verify publisher.pub -signature SHA256SUMS.sig SHA256SUMS
cat SHA256SUMS
```

The manifest has one line: the digest of `fleet-agent`, two spaces and the file name. The name has no directory, so `sha256sum --check` looks for `fleet-agent` in the current directory. Run the check once inside each cache:

```sh
for cache in cache-1 cache-2 cache-3; do
  echo "== $cache"
  (cd /var/cache/fleet/$cache && sha256sum --check /var/lib/fleet-release/SHA256SUMS)
done
```

One cache reports `fleet-agent: OK`. The other two report `FAILED`: one copy has a single changed byte, the other is a different file of the same size.

`install` copies a file and sets its owner, group and mode in one step, so the file never exists with the wrong permissions. It also replaces the unverified copy. Replace `<CACHE>` with the cache that passed:

```sh
install -o root -g root -m 0755 /var/cache/fleet/<CACHE>/fleet-agent /opt/fleet/bin/fleet-agent
```

A check at the download location says nothing about the file that will run, so check the installed copy at its final location:

```sh
(cd /opt/fleet/bin && sha256sum --check /var/lib/fleet-release/SHA256SUMS)
stat -c '%a %U:%G %n' /opt/fleet /opt/fleet/bin /opt/fleet/bin/fleet-agent
exit
```

The first command must print `fleet-agent: OK`. The second must print `755 root:root` for all three paths.

## Step 4: record the result (check `install-record`)

Back on your machine, replace `<CACHE>` with the cache name and `<DIGEST>` with the digest from `SHA256SUMS`. Save this as `configmap-install-record.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: install-record
  namespace: starfleet-031-050-01-03
data:
  cache: "<CACHE>"
  sha256: "<DIGEST>"
```

Apply it:

```sh
kubectl apply -f configmap-install-record.yaml
```

## Step 5: test the record

Print both keys:

```sh
kubectl -n starfleet-031-050-01-03 get configmap install-record -o jsonpath='{.data.cache}{"\n"}{.data.sha256}{"\n"}'
```

The first line must show the cache that printed `fleet-agent: OK` in Step 3. The second line must show the digest from `SHA256SUMS`.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not stop at the file. The grader also checks `/opt/fleet` and `/opt/fleet/bin`: each must be owned by `root` and must not be writable by group or others.
>
> Do not copy the file with `cp` and forget the owner or the mode. The installed `fleet-agent` must be `root:root` with mode `0755`.
>
> Do not trust a cache copy before you verify the signature of `SHA256SUMS`. A digest is only worth something when the manifest it comes from is authentic.
>
> Write the cache name in the form `cache-2`, not the full path.
