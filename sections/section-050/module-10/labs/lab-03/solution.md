---
exam_objectives:
- Verify platform binaries before deploying
---
# Install A Verified Binary Into A Protected Directory: Solution

Connect to the lab first, so that `kubectl` talks to this lab's cluster and `$node_name` names its control plane node:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-01-03)"
node_name="astro-ats-031-lab-050-01-03-control-plane"
RELEASE=/var/lib/fleet-release
```

## Authenticate the manifest

Verify the signature before you use any digest from the manifest. `openssl dgst -sha256 -verify` prints `Verified OK` when the publisher's private key signed exactly this manifest:

```sh
podman exec "$node_name" openssl dgst -sha256 -verify $RELEASE/publisher.pub -signature $RELEASE/SHA256SUMS.sig $RELEASE/SHA256SUMS
podman exec "$node_name" cat $RELEASE/SHA256SUMS
```

The manifest has one line: the digest of `fleet-agent`, two spaces and the file name.

## Find the genuine copy

The manifest names the file without a directory, so `sha256sum --check` looks for `fleet-agent` in the current directory. Run the check once inside each cache:

```sh
podman exec -w /var/cache/fleet/cache-1 "$node_name" sha256sum --check $RELEASE/SHA256SUMS
podman exec -w /var/cache/fleet/cache-2 "$node_name" sha256sum --check $RELEASE/SHA256SUMS
podman exec -w /var/cache/fleet/cache-3 "$node_name" sha256sum --check $RELEASE/SHA256SUMS
```

One cache reports `fleet-agent: OK`. The other two report `FAILED`: one copy has a single changed byte, the other is a different file of the same size.

## Install and protect

First take the directories back from user 1000, so nobody else can swap the file after you install it. Look at the starting state, then fix the owner and the mode:

```sh
podman exec "$node_name" stat -c '%a %U:%G %n' /opt/fleet /opt/fleet/bin /opt/fleet/bin/fleet-agent
podman exec "$node_name" chown root:root /opt/fleet /opt/fleet/bin
podman exec "$node_name" chmod 0755 /opt/fleet /opt/fleet/bin
```

`install` copies a file and sets its owner, group and mode in one step, so the file never exists with the wrong permissions. It also replaces the unverified copy. The example uses `cache-2`; use the cache that passed:

```sh
podman exec "$node_name" install -o root -g root -m 0755 /var/cache/fleet/cache-2/fleet-agent /opt/fleet/bin/fleet-agent
podman exec "$node_name" stat -c '%a %U:%G %n' /opt/fleet /opt/fleet/bin /opt/fleet/bin/fleet-agent
```

The second command now prints `755 root:root` for all three paths.

## Verify at the final location and record

A check at the download location says nothing about the file that will run. Check the installed copy:

```sh
podman exec -w /opt/fleet/bin "$node_name" sha256sum --check $RELEASE/SHA256SUMS
TRUSTED_DIGEST=$(podman exec "$node_name" cut -d' ' -f1 $RELEASE/SHA256SUMS)
kubectl -n starfleet-031-050-01-03 create configmap install-record \
  --from-literal=cache=cache-2 --from-literal=sha256="$TRUSTED_DIGEST"
```

The grader verifies the signature again, computes the digest of `/opt/fleet/bin/fleet-agent`, and checks the owner and mode of the file and both directories.
