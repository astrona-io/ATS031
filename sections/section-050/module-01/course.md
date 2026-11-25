# Verify Platform Binaries Before Deploying

Every Kubernetes node runs binaries that you downloaded from somewhere: `kubelet`, `kubeadm`, `kubectl` and the container runtime. Each of them runs with high privilege. If someone replaces one of these files on its way to the node, the attacker gets that privilege. This can happen through a compromised mirror, an intercepted download or a poisoned build pipeline.

Verification is the step that closes this gap. It makes sure that the bytes you are about to run are the same bytes that the publisher released. A publisher is the project or company that builds and releases the software.

There are two kinds of check. One kind detects that a file has changed. The other kind proves who published the file. This module gives you the commands for both: `sha256sum` for digests, `openssl` for a signature made with a key, and `cosign` for a signature made with an identity. You practise `sha256sum` and `openssl` in the playground on a staged set of test files. The `cosign` check is shown as reference only, because the playground has no network path to the real Kubernetes release servers.

## What you will learn

After this module, you can:

- explain what a checksum proves, what it does not prove, and why the source of the expected digest decides how much it is worth;
- choose the exact artifact by version, operating system and CPU architecture, and record its digest;
- verify a signature over a checksum manifest with a public key, and then check the binary against that trusted manifest;
- show that a forged checksum file matches a tampered binary, and that signature verification rejects the forged file;
- keep the verified bytes tied to what you deploy, and explain what verification does not cover.

## How the module is laid out

You start with **Integrity, Authenticity And The Exact Artifact**, which explains the questions that verification answers and how to pick the right file. **Digests At Work And The Limits Of A Checksum** then computes digests in the playground and shows how a forged checksum file fools a bare check. **Verify A Signed Manifest And Record The Result** checks the signature on the manifest, rejects the forgery and stores the result in the cluster. **Keep The Binding Through Delivery, And Identity-Based Signatures** closes the module with how to protect the file after the check and how identity-based signatures work.

A lab follows each hands-on part, so you can practise the skill right away.

## Before you start

You should know the basics of the Linux command line, such as listing files, reading a file and running a command in a container. You should also be able to use `kubectl get` and `kubectl create`.

## Your playground

Your playground is a `kind` cluster that runs Kubernetes v1.35, with one control plane node and one worker node. The cluster already runs these objects:

| Namespace | Object | What it is |
| --- | --- | --- |
| `starfleet` | `probe-code` ConfigMap | Holds the Python code of the small web server |
| `starfleet` | `probe` Deployment, two pods, labels `app: probe` and `release: probe` | A small web server that listens on port 8080 |
| `starfleet` | `probe` Service | Port 80, forwards to port 8080 of the `probe` pods |
| `starfleet` | `shuttle` pod, label `app: shuttle` | A client pod with `busybox` tools |
| `outpost` | `drifter` pod, label `app: drifter` | A client pod with `busybox` tools, in another namespace |

The files you verify do not live in the cluster. They sit in the container of the control plane node, in the directory `/var/lib/training-release`:

| File | What it is |
| --- | --- |
| `kubectl` | The binary to deploy |
| `kubectl-tampered` | A copy of the binary with extra bytes added at the end |
| `checksums.txt` | A manifest with the SHA-256 digest of `kubectl` |
| `checksums.sig` | A signature over `checksums.txt` |
| `publisher.pub` | The public key that checks the signature |

The key was made only for this exercise. It plays the role of a publisher key, and it is not the key of the real Kubernetes project.

`kubectl` already points at the playground cluster. Start your playground now and keep it running while you read:

<!-- astrona:playground -->
