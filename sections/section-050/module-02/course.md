---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify Kubernetes Release Binaries Hands-On

A node runs `kubelet`, an operator runs `kubectl` and `kubeadm`, and each of them arrives as a file that someone published. The exam asks a practical question about these files: given a downloaded binary and a published checksum, is the binary the one the project released, and if not, what is wrong with it? This module drills that question with the commands you would use, against a staged copy of the Kubernetes release layout.

## Learning objectives

After this module you can:

- Build the download address of a release binary from the version, the operating system and the CPU architecture, and name the checksum file that belongs to it.
- Verify a binary with `sha256sum --check` using the exact `hash  filename` format, and read the exit status.
- Decide whether a mismatch means changed bytes, a wrong architecture, a wrong version or a stale checksum file.
- Read the version, commit and platform of `kubectl`, `kubeadm` and `kubelet`, and compare them with what the file claims to be.
- Check the `kubelet` that is running on a node against the published digest for its version.

## Before you start

You need Linux command line basics, `kubectl` and `podman`. The module has five parts. The first describes the release artifacts and their addresses. The second covers `sha256sum --check` and its input format. The third finds out why a file fails. The fourth reads the version that a binary reports. The fifth checks the binary that runs on a node.

Your playground is a `kind` cluster with one control plane node and one worker node. It has no path to `dl.k8s.io`. Instead, the control plane node container holds an offline mirror in `/var/lib/training-release/k8s`, built with the same paths as the real release site:

| Path | What it holds |
| --- | --- |
| `release/stable.txt` | The version string of the staged stable release |
| `release/<version>/bin/linux/<architecture>/` | The binaries `kubectl`, `kubeadm` and `kubelet` with a `.sha256` file for each |
| `current` | A link to the directory for this node's version and architecture |
| `downloads/` | Files you will verify: some genuine, some not |

The newer release holds copies of the binaries that the node image installed. The older release and the other architecture hold small stand-in files, so that digests differ. The mirror is built when the playground starts, and every digest in it is computed at that moment. Real addresses appear in the text as reference only.

Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
