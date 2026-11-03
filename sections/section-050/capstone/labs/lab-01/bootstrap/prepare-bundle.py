#!/usr/bin/env python3
"""Stage the capstone release bundle on the control plane node.

Usage: prepare-bundle.py <cluster-name>

The bundle holds two stand-in binaries, a manifest that also lists the digest of
the kubelet that runs on the worker, a signature over the manifest, the public
key and an image reference. One of the two binaries is changed after the
manifest was signed. All digests and keys are made here at run time.
"""
import random
import subprocess
import sys

CLUSTER = sys.argv[1]
CONTEXT = "kind-astro-" + CLUSTER
CONTROL = "astro-%s-control-plane" % CLUSTER
WORKER = "astro-%s-worker" % CLUSTER


def run(*args):
    result = subprocess.run(args, text=True, capture_output=True, timeout=300)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.exit("Command failed: " + " ".join(args[:4]))
    return result.stdout.strip()


assert run("kubectl", "config", "current-context") == CONTEXT, "Select the private environment"
for name in (CONTROL, WORKER):
    label = run("podman", "inspect", name, "--format", '{{index .Config.Labels "io.x-k8s.kind.cluster"}}')
    assert label == "astro-" + CLUSTER, "Refusing an unrelated node container"

worker_digest = run("podman", "exec", WORKER, "sh", "-c", "sha256sum /usr/bin/kubelet | cut -d' ' -f1")
victim = random.choice(["kubectl", "kubeadm"])

SCRIPT = r"""
B=/var/lib/training-release/bundle
rm -rf "$B" /var/lib/training-release/approved
mkdir -p "$B" /var/lib/training-release/approved
for tool in kubectl kubeadm; do
  head -c 131072 /dev/urandom > "$B/$tool"
done
: > "$B/SHA256SUMS"
for tool in kubectl kubeadm; do
  printf '%s  %s\n' "$(sha256sum "$B/$tool" | cut -d' ' -f1)" "$tool" >> "$B/SHA256SUMS"
done
printf '%s  %s\n' "$1" kubelet >> "$B/SHA256SUMS"
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out /tmp/bundle-publisher.key
openssl pkey -in /tmp/bundle-publisher.key -pubout -out "$B/publisher.pub"
openssl dgst -sha256 -sign /tmp/bundle-publisher.key -out "$B/SHA256SUMS.sig" "$B/SHA256SUMS"
rm -f /tmp/bundle-publisher.key
printf 'docker.io/library/busybox:1.37.0\n' > "$B/image.txt"
printf 'altered' >> "$B/$2"
"""
run("podman", "exec", CONTROL, "sh", "-ec", SCRIPT, "_", worker_digest, victim)
print("Release bundle staged")
