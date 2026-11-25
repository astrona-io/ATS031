# Verify Kubernetes Release Binaries Hands-On

A Kubernetes cluster runs on a few programs that you download as files. Every node runs `kubelet`, the agent that starts and watches the pods on that node. An operator uses `kubectl`, the command line client, and `kubeadm`, the tool that sets up a cluster. Someone published each of these files, and you must trust them before you run them.

The exam asks a practical question about these files. You get a downloaded binary and a published checksum. Is the binary the one the project released? And if it is not, what is wrong with it? A checksum, or digest, is a short fixed-length value that a hash function computes from the bytes of a file. If one byte changes, the digest changes too.

This module practises that question with the real commands. You work on a staged copy of the Kubernetes release layout, so every check runs without a network path to the release site.

## What you will learn

After this module, you can:

- build the download address of a release binary from the version, the operating system and the CPU architecture, and name the checksum file that belongs to it;
- verify a binary with `sha256sum --check` using the exact `hash  filename` format, and read the exit status;
- decide whether a mismatch means changed bytes, a wrong architecture, a wrong version or a stale checksum file;
- read the version, commit and platform of `kubectl`, `kubeadm` and `kubelet`, and compare them with what the file claims to be;
- check the `kubelet` that is running on a node against the published digest for its version.

## How the module is laid out

You start with **Kubernetes Release Artifacts**, which explains where the project publishes its binaries and which checksum file belongs to which binary. **sha256sum And The Check Format** then verifies a binary and shows the strict line format the tool reads. **Detect A Tampered Or Wrong Binary** takes a failed check and finds out what the bytes really are. **Read The Version Of A Binary** compares the version a program prints with its name and its digest. **Verify What Runs On A Node** closes the module by checking the `kubelet` that is running right now.

A lab follows each part, so you can practise the skill right away.

## Before you start

You should know the Linux command line basics: files, directories, pipes and exit status. You should also be able to use `kubectl` and `podman`.

## Your playground

Your playground is a `kind` cluster that runs Kubernetes v1.35, with one control plane node and one worker node. The cluster has no path to `dl.k8s.io`, the real release site. Instead, the control plane node container holds an offline mirror in `/var/lib/training-release/k8s`. The mirror uses the same paths as the real release site:

| Path | What it holds |
| --- | --- |
| `release/stable.txt` | The version string of the staged stable release |
| `release/<version>/bin/linux/<architecture>/` | The binaries `kubectl`, `kubeadm` and `kubelet` with a `.sha256` file for each |
| `current` | A link to the directory for this node's version and architecture |
| `other-arch` | A link to the directory for the same version and the other architecture |
| `downloads/` | Files you will verify: some genuine, some not |

The newer release holds copies of the binaries that the node image installed. The older release and the other architecture hold small stand-in files, so that their digests differ. The playground builds the mirror when it starts, and it computes every digest at that moment. Real addresses appear in the text as reference only.

The cluster also runs these workloads. The commands in this module work on the node containers and do not use them:

| Namespace | Object | What it is |
| --- | --- | --- |
| `starfleet` | `probe-code` ConfigMap | Holds `server.py`, the code of the small web server |
| `starfleet` | `probe` Deployment, two pods, labels `app: probe` and `release: probe` | A small web server that listens on port 8080 |
| `starfleet` | `probe` Service | Port 80, forwards to port 8080 of the `probe` pods |
| `starfleet` | `shuttle` pod, label `app: shuttle` | A client pod based on `busybox` |
| `outpost` | `drifter` pod, label `app: drifter` | A client pod based on `busybox`, in another namespace |

Start your playground now and keep it running while you read:

<!-- astrona:playground -->
