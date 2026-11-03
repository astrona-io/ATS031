---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify Kubernetes Release Binaries Playground

This playground is a private `kind` cluster with Kubernetes v1.35, one control plane node and one worker node. Nothing in it needs a network path to the outside.

The control plane node holds an offline mirror in `/var/lib/training-release/k8s`. It follows the layout of the Kubernetes release site: `release/stable.txt`, `release/<version>/bin/linux/<architecture>/` with a `.sha256` file for each binary, a `current` link to the version in use, and a `downloads` directory with files to verify. The bootstrap computed every digest when it started. The mirror holds genuine files, a tampered file, a file for the other architecture and a checksum file of the older version.

Use a host shell with the private kubeconfig. Each deep-dive part of the module tells you when to open it.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-playground-050-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-playground-050-02" || exit 1
CONTROL=astro-ats-031-playground-050-02-control-plane
WORKER=astro-ats-031-playground-050-02-worker
```

Host-level commands name only the node containers of this environment. They never operate on the host operating system.

The worker node runs the `kubelet` that part of the exercises check. The real download addresses are reference only, because the nodes have no network path to the release site.
