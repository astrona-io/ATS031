# Verify platform binaries before deploying

A binary arrives on a node and runs with high privilege. If someone changed it on the way, the whole node is theirs. A checksum that comes from the same place as the file does not help much: it only proves that the download arrived in one piece, not that it came from the real publisher.

Two different questions hide here. Integrity asks whether the bytes changed. Authenticity asks who made them. In this section, you learn to tell the two apart, to verify a signed manifest and then the binary against it, and to keep the verified bytes tied to what you actually deploy.

## What you will learn

The section moves from one file to packages and images:

- **Verify Platform Binaries Before Deploying.** Integrity and authenticity, digests, a signed manifest, and keeping the verified bytes tied to what is deployed.
- **Verify Kubernetes Release Binaries Hands-On.** The release layout, the `sha256sum --check` format, tampered files and files for the wrong architecture, binary versions, and the `kubelet` that runs on a node.
- **Verify Packages, Images And Signatures.** Signed package repositories, package verification, cosign with a local key pair, keyless verification, image digests and pinning, and verification when an object is admitted to the cluster.

## How this section works

Each module has its own playground: a private `kind` cluster that runs Kubernetes v1.35 with no path to the outside network. Start it from the first page of the module and keep it running while you read, because every page has commands to try.

When a page teaches a skill you can be graded on, a lab comes right after it. A lab gives you a short task in a fresh cluster and checks your result. Each module ends with a summary and a short knowledge check.

## By the end of this section

You will be able to:

- explain what a checksum proves, what it does not prove, and why the source of the expected digest decides its value;
- choose the exact artifact by version, operating system and architecture, and record its digest;
- verify a signature over a checksum manifest with a public key, and check the binary against the verified manifest;
- show that a forged checksum file matches a tampered binary, and that signature verification rejects the forgery;
- keep the verified bytes tied to what is deployed, and explain what verification does not cover;
- build the checksum check for a Kubernetes release file in the exact `digest  file name` form, and read its exit status;
- detect a tampered file, a file for the wrong architecture and a stale checksum file;
- read the version of `kubectl`, `kubeadm` and `kubelet`, and verify the binary that a node runs through `/proc/<pid>/exe`;
- verify GPG and cosign signatures with a local key, and explain what keyless verification and package verification add;
- pin an image by digest and compare it with the `imageID` of the running pod.
