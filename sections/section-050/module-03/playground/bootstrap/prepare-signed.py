#!/usr/bin/env python3
"""Stage signed fixtures: a GPG key and signature, and a cosign key pair and signature.

Usage: prepare-signed.py <cluster-name> <playground|lab1>

Keys are generated here at run time inside the control plane node container.
The private keys are deleted after signing. If gpg or cosign cannot be made
available on the node, the script prints a warning and writes a marker file
instead of failing in the playground; in lab mode it fails.
"""
import random
import subprocess
import os
import sys

ENGINE = os.environ.get("ASTRONA_CONTAINER_ENGINE") or "podman"

CLUSTER = sys.argv[1]
MODE = sys.argv[2]
CONTEXT = "kind-astro-" + CLUSTER
CONTROL = "astro-%s-control-plane" % CLUSTER


def run(*args, check=True):
    result = subprocess.run(args, text=True, capture_output=True, timeout=900)
    if check and result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.exit("Command failed: " + " ".join(args[:4]))
    return result


assert run("kubectl", "config", "current-context").stdout.strip() == CONTEXT, "Select the private environment"
label = run(ENGINE, "inspect", CONTROL, "--format", '{{index .Config.Labels "io.x-k8s.kind.cluster"}}').stdout.strip()
assert label == "astro-" + CLUSTER, "Refusing an unrelated node container"


def node(script, check=True):
    return run(ENGINE, "exec", CONTROL, "sh", "-c", script, check=check)


# 1. Make the tools available. The node image may lack gpg. cosign is fetched
#    from the project release page when the node has a network path. The
#    version is pinned: cosign 3 signs into a bundle by default and rejects the
#    --output-signature flags used below.
tools = node(r"""
S=/var/lib/training-release/signed
mkdir -p "$S"
rm -f "$S"/NO-GPG "$S"/NO-COSIGN
if ! command -v gpg >/dev/null 2>&1; then
  (apt-get update -qq && apt-get install -y -qq gnupg) >/dev/null 2>&1 || true
fi
command -v gpg >/dev/null 2>&1 || touch "$S/NO-GPG"
if ! command -v cosign >/dev/null 2>&1; then
  # SHA-256 sums from cosign_checksums.txt of the v2.4.1 release.
  case "$(uname -m)" in
    x86_64) A=amd64; SUM=8b24b946dd5809c6bd93de08033bcf6bc0ed7d336b7785787c080f574b89249b ;;
    aarch64) A=arm64; SUM=3b2e2e3854d0356c45fe6607047526ccd04742d20bd44afb5be91fa2a6e7cb4a ;;
  esac
  curl -fsSL -o /tmp/cosign "https://github.com/sigstore/cosign/releases/download/v2.4.1/cosign-linux-$A" >/dev/null 2>&1 \
    && echo "$SUM  /tmp/cosign" | sha256sum -c - >/dev/null 2>&1 \
    && install -m 0755 /tmp/cosign /usr/local/bin/cosign \
    && sha256sum /usr/local/bin/cosign > "$S/cosign.fetched.sha256" || true
  rm -f /tmp/cosign
fi
command -v cosign >/dev/null 2>&1 || touch "$S/NO-COSIGN"
ls "$S"
""").stdout
missing_gpg = "NO-GPG" in tools
missing_cosign = "NO-COSIGN" in tools
if MODE != "playground" and (missing_gpg or missing_cosign):
    sys.exit("gpg and cosign are both required for this lab and could not be staged")
if missing_gpg:
    print("WARNING: gpg is not available on the node; the GPG exercises become reading only")
if missing_cosign:
    print("WARNING: cosign is not available on the node; the cosign exercises become reading only")

GPG_FIXTURE = r"""
S=/var/lib/training-release/signed
D="$1"
mkdir -p "$D"
H=$(mktemp -d); chmod 700 "$H"; export GNUPGHOME="$H"
gpg --batch --pinentry-mode loopback --passphrase '' --quick-generate-key 'Training Publisher <publisher@training.invalid>' rsa3072 sign never >/dev/null 2>&1
gpg --export > "$D/publisher.gpg"
gpg --armor --export > "$D/publisher.asc"
printf 'release notes for the training fixture\nline two\n' > "$D/$2"
gpg --armor --detach-sign --output "$D/$2.asc" "$D/$2"
if [ -n "$3" ]; then
  # Repository-style files: a Release file that lists the digest of a Packages file.
  printf 'package list stand-in\n' > "$D/Packages"
  printf 'Suite: training\nSHA256:\n %s %s Packages\n' "$(sha256sum "$D/Packages" | cut -d' ' -f1)" "$(wc -c < "$D/Packages" | tr -d ' ')" > "$D/Release"
  gpg --armor --detach-sign --output "$D/Release.gpg" "$D/Release"
fi
rm -rf "$H"
"""

COSIGN_FIXTURE = r"""
D="$1"
mkdir -p "$D"
W=$(mktemp -d)
(cd "$W" && COSIGN_PASSWORD='' cosign generate-key-pair >/dev/null 2>&1)
cp "$W/cosign.pub" "$D/cosign.pub"
printf 'build record for the training fixture\n' > "$D/$2"
COSIGN_PASSWORD='' cosign sign-blob --yes --key "$W/cosign.key" --tlog-upload=false --output-signature "$D/$2.sig" "$D/$2" >/dev/null 2>&1
rm -rf "$W"
"""

if MODE == "playground":
    base = "/var/lib/training-release/signed"
    if not missing_gpg:
        node("sh -ec '%s' _ %s release-notes.txt repo" % (GPG_FIXTURE.replace("'", "'\\''"), base))
        node("cp %s/release-notes.txt %s/release-notes-forged.txt && printf 'extra line\\n' >> %s/release-notes-forged.txt" % (base, base, base))
    if not missing_cosign:
        node("sh -ec '%s' _ %s build-record.txt" % (COSIGN_FIXTURE.replace("'", "'\\''"), base))
        node("cp %s/build-record.txt %s/build-record-forged.txt && printf 'extra line\\n' >> %s/build-record-forged.txt" % (base, base, base))
elif MODE == "lab1":
    base = "/var/lib/training-release/signed/lab"
    node("rm -rf %s" % base)
    node("sh -ec '%s' _ %s gpg-notes.txt" % (GPG_FIXTURE.replace("'", "'\\''"), base))
    node("sh -ec '%s' _ %s cosign-notes.txt" % (COSIGN_FIXTURE.replace("'", "'\\''"), base))
    forged = random.choice(["gpg-notes.txt", "cosign-notes.txt"])
    node("printf 'changed after signing\\n' >> %s/%s" % (base, forged))
else:
    sys.exit("Unknown mode")
print("Signed fixtures staged for mode " + MODE)
