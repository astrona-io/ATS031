# Verify Packages, Images And Signatures

Cluster software reaches a node in three ways: as operating system packages, as standalone binaries and as container images. If an attacker changes any of them on the way, the cluster runs the attacker's code. So before you install or run something, you want to know two things: that it did not change, and who stands behind it.

A checksum answers the first question. It is a short value computed from the bytes of a file, so a changed file gives a different value. A signature answers the second question. It shows which key, or which identity, vouched for the file.

Each channel has its own signing tools. GPG (the GNU Privacy Guard) signs package repositories. cosign signs single files and container images. An image digest names the exact content of an image, so you can pin what runs.

## What you will learn

After this module, you can:

- verify a detached GPG signature over a file and over a repository `Release` file, and read the result;
- verify a file signature with cosign and a local public key, and explain how keyless verification uses a certificate identity and an issuer;
- find the digest of an image, pin a Deployment to it and compare it with the image identifier that a running pod reports;
- explain what a software bill of materials lists, and what verification at admission does and does not prove.

## How the module is laid out

You start with **GPG Signed Repositories**, which shows how one signature protects a whole package repository and how to check it with `gpg` and `gpgv`. **Package Verification On A Node** then checks files that a package already installed, and shows which files that check cannot see. **cosign With A Local Key Pair** verifies and creates signatures on single files.

**Keyless Verification And Release Signatures** explains signing without a long lived private key, and how the Kubernetes project signs its release files. This part is reading only, because it needs public servers that the playground cannot reach. **Image Digests And Pinning** ties a running container to an exact image. **SBOMs And Admission-Time Verification** closes the module with component lists and with rules that the API server enforces when a pod is created.

A lab follows each part that has hands-on steps, so you can practise the skill right away.

## Before you start

You should know the Linux command line basics. You should also be able to use `kubectl` and `podman`.

## Your playground

Your playground is a `kind` cluster that runs Kubernetes v1.35, with one control plane node and one worker node. The cluster already runs these workloads:

| Namespace | Object | What it is |
| --- | --- | --- |
| `starfleet` | Namespace, label `project: ckad` | The namespace for the main example workloads |
| `outpost` | Namespace, label `project: outpost` | A second namespace |
| `starfleet` | `probe-code` ConfigMap | Holds `server.py`, the code of the `probe` web server |
| `starfleet` | `probe` Deployment, two pods, labels `app: probe` and `release: probe` | A small web server on the `python:3.13-alpine` image that listens on port 8080 |
| `starfleet` | `probe` Service | Port 80, forwards to port 8080 of the `probe` pods |
| `starfleet` | `shuttle` pod, label `app: shuttle` | A client pod on the `busybox:1.37.0` image |
| `outpost` | `drifter` pod, label `app: drifter` | A client pod on the `busybox:1.37.0` image, in another namespace |
| `starfleet` | `relay` Deployment, one pod, label `app: relay` | Runs the `busybox:1.37.0` image by tag, for the image exercises |

The control plane node container also holds fixtures in `/var/lib/training-release/signed`. The bootstrap creates every key when the playground starts, and it deletes the private keys after signing. The playground has no network path to the real Kubernetes package repository.

| File | What it is |
| --- | --- |
| `publisher.asc`, `publisher.gpg` | The public GPG key, in text form and in keyring form |
| `release-notes.txt`, `release-notes.txt.asc` | A file and its detached GPG signature |
| `release-notes-forged.txt` | A copy of the file with a line added after signing |
| `Release`, `Release.gpg`, `Packages` | A repository-style file list and its detached signature |
| `cosign.pub` | The public key of a cosign key pair |
| `build-record.txt`, `build-record.txt.sig` | A file and its cosign signature |
| `build-record-forged.txt` | A copy of the file with a line added after signing |

The tools `gpg` and `cosign` run on the control plane node. If the node image does not have them, the bootstrap tries to install `gpg` from the package repositories. It also tries to download `cosign` from the release page of the cosign project, which needs a network path from the node.

If that fails, the bootstrap writes a marker file named `NO-GPG` or `NO-COSIGN` in the fixture directory. The matching exercises are then reading only. When the bootstrap downloads `cosign`, it records the binary with its digest in `cosign.fetched.sha256`. That file only records what was downloaded; it does not prove that the download is genuine. All keys are fixtures and are not keys of any real project.

`kubectl` already points at the playground cluster. Start your playground now and keep it running while you read:

<!-- astrona:playground -->
