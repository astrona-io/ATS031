---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify Packages, Images And Signatures Playground

This playground is a private `kind` cluster with Kubernetes v1.35, one control plane node and one worker node. Nothing in it needs a network path to the outside.

The control plane node holds signed fixtures in `/var/lib/training-release/signed`: a GPG key and signed files, a cosign key pair and a signed build record, and a forged copy of each. The bootstrap generated every key and signature when it started and deleted the private keys. If `gpg` or `cosign` could not be installed on the node, the bootstrap wrote a file named `NO-GPG` or `NO-COSIGN`, and the matching exercises are reading only.

Use a host shell with the private kubeconfig. Each deep-dive part of the module tells you when to open it.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-playground-050-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-playground-050-03" || exit 1
CONTROL=astro-ats-031-playground-050-03-control-plane
WORKER=astro-ats-031-playground-050-03-worker
```

Host-level commands name only the node containers of this environment. They never operate on the host operating system.

A Deployment named `relay` in the `starfleet` namespace runs the `busybox:1.37.0` image by tag. The image exercises use it.
