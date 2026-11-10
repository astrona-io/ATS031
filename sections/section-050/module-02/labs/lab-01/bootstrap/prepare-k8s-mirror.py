#!/usr/bin/env python3
"""Stage the offline Kubernetes release mirror and its download fixtures.

Usage: prepare-k8s-mirror.py <cluster-name> <playground|lab1|lab2>

All digests are computed here at run time inside the node containers.
Nothing is downloaded, and no digest is written in advance.
"""
import os
import random
import subprocess
import sys
CONTEXT = os.environ.get('ASTRONA_KUBE_CONTEXT') or 'kind-astro-ats-031-lab-050-02-01'
if subprocess.run(['kubectl', 'config', 'current-context'], capture_output=True, text=True).stdout.strip() != CONTEXT:
    sys.exit('Refusing to operate on another Kubernetes context')

# The cluster comes from the environment astrona sets; the argument is the fallback.
CLUSTER = os.environ.get("ASTRONA_KIND_CLUSTER") or "astro-" + sys.argv[1]
MODE = sys.argv[2]
ENGINE = os.environ.get("ASTRONA_CONTAINER_ENGINE") or "podman"
CONTROL = CLUSTER + "-control-plane"
WORKER = CLUSTER + "-worker"


def run(*args):
    result = subprocess.run(args, text=True, capture_output=True, timeout=600)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.exit("Command failed: " + " ".join(args[:4]))
    return result.stdout.strip()


for name in (CONTROL, WORKER):
    label = run(ENGINE, "inspect", name, "--format", '{{index .Config.Labels "io.x-k8s.kind.cluster"}}')
    assert label == CLUSTER, "Refusing an unrelated node container"


def node(name, script):
    return run(ENGINE, "exec", name, "sh", "-ec", script)


# Shell fragment shared by the modes. It sets the version, the node architecture
# and the architecture that does not match this node.
COMMON = r"""
R=/var/lib/training-release/k8s
VER=v1.35.0
OLD=v1.34.0
[ "$(kubelet --version)" = "Kubernetes $VER" ] || { echo "Node image does not run $VER" >&2; exit 1; }
case "$(uname -m)" in
  x86_64) A=amd64; O=arm64 ;;
  aarch64) A=arm64; O=amd64 ;;
  *) echo "Unsupported architecture" >&2; exit 1 ;;
esac
digest() { sha256sum "$1" | cut -d' ' -f1 | tr -d '\n'; }
"""

PLAYGROUND = COMMON + r"""
rm -rf "$R"
for dir in "$VER/bin/linux/$A" "$VER/bin/linux/$O" "$OLD/bin/linux/$A"; do
  mkdir -p "$R/release/$dir"
done
mkdir -p "$R/downloads"
printf '%s' "$VER" > "$R/release/stable.txt"

# Genuine files: copies of the binaries that the node image installed.
for tool in kubectl kubeadm kubelet; do
  cp "/usr/bin/$tool" "$R/release/$VER/bin/linux/$A/$tool"
  digest "$R/release/$VER/bin/linux/$A/$tool" > "$R/release/$VER/bin/linux/$A/$tool.sha256"
done

# Stand-in files for the older release and for the other architecture.
# They are small text files; only their digests are used.
for tool in kubectl kubeadm kubelet; do
  printf 'stand-in for %s %s linux/%s\n' "$tool" "$OLD" "$A" > "$R/release/$OLD/bin/linux/$A/$tool"
  digest "$R/release/$OLD/bin/linux/$A/$tool" > "$R/release/$OLD/bin/linux/$A/$tool.sha256"
done
printf 'stand-in for kubectl %s linux/%s\n' "$VER" "$O" > "$R/release/$VER/bin/linux/$O/kubectl"
digest "$R/release/$VER/bin/linux/$O/kubectl" > "$R/release/$VER/bin/linux/$O/kubectl.sha256"

# Convenience links for the exercises.
ln -sfn "$R/release/$VER/bin/linux/$A" "$R/current"
ln -sfn "$R/release/$VER/bin/linux/$O" "$R/other-arch"

# Downloads to verify.
# kubectl: the genuine bytes with the matching checksum file.
ln -f "$R/current/kubectl" "$R/downloads/kubectl" 2>/dev/null || cp "$R/current/kubectl" "$R/downloads/kubectl"
cp "$R/current/kubectl.sha256" "$R/downloads/kubectl.sha256"
# kubeadm: the checksum file is genuine, the bytes have one extra appended string.
cp "$R/current/kubeadm" "$R/downloads/kubeadm"
printf 'altered' >> "$R/downloads/kubeadm"
cp "$R/current/kubeadm.sha256" "$R/downloads/kubeadm.sha256"
# kubelet: the bytes are genuine, the checksum file is the one of the older release.
ln -f "$R/current/kubelet" "$R/downloads/kubelet" 2>/dev/null || cp "$R/current/kubelet" "$R/downloads/kubelet"
cp "$R/release/$OLD/bin/linux/$A/kubelet.sha256" "$R/downloads/kubelet.sha256"
# A kubectl for the other architecture, paired with the checksum file for this one.
cp "$R/other-arch/kubectl" "$R/downloads/kubectl-$O"
cp "$R/current/kubectl.sha256" "$R/downloads/kubectl-$O.sha256"
# A copy that claims to be the older release but holds the newer bytes.
cp "$R/current/kubectl" "$R/downloads/kubectl-claimed-$OLD"
cp "$R/release/$OLD/bin/linux/$A/kubectl.sha256" "$R/downloads/kubectl-claimed-$OLD.sha256"
"""

LAB1 = COMMON + r"""
rm -rf "$R"
mkdir -p "$R/lab"
for tool in kubectl kubeadm kubelet; do
  head -c 262144 /dev/urandom > "$R/lab/$tool"
  digest "$R/lab/$tool" > "$R/lab/$tool.sha256"
done
"""

LAB2 = COMMON + r"""
rm -rf "$R"
for dir in "$VER/bin/linux/$A" "$OLD/bin/linux/$A"; do
  mkdir -p "$R/release/$dir"
done
digest /usr/bin/kubelet > "$R/release/$VER/bin/linux/$A/kubelet.sha256"
printf 'stand-in for kubelet %s linux/%s\n' "$OLD" "$A" > /tmp/kubelet-older
digest /tmp/kubelet-older > "$R/release/$OLD/bin/linux/$A/kubelet.sha256"
rm -f /tmp/kubelet-older
"""

if MODE == "playground":
    node(CONTROL, PLAYGROUND)
elif MODE == "lab1":
    node(CONTROL, LAB1)
    victim = random.choice(["kubectl", "kubeadm", "kubelet"])
    node(CONTROL, "printf altered >> /var/lib/training-release/k8s/lab/%s" % victim)
elif MODE == "lab2":
    # The release checksums are staged on the worker, where the check runs.
    node(WORKER, LAB2)
else:
    sys.exit("Unknown mode")
print("Release mirror staged for mode " + MODE)
