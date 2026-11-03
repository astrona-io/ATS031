---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Package Verification On A Node

A signature check happens at install time. Later, a file that a package installed can be changed on disk. This part explains how the package manager can compare installed files with the package metadata. It is reading only, for a reason given below, and it has no commands to run.

## What the package manager remembers

When dpkg installs a Debian package, it records the list of files and, for many of them, an MD5 digest from the package. The command `dpkg --verify`, also written `dpkg -V`, compares the files on disk with that record and prints one line for each file that differs. Each line starts with nine characters. A `5` in the third place means that the content digest differs, and other positions mean a changed size, mode, owner or time. A question mark means that the check could not be done for that property. After the flags comes a letter `c` for configuration files, and then the path. A clean system prints nothing.

The tool `debsums` does a similar job with the digests stored in the package files. On RPM based systems the command `rpm -V` prints the same kind of nine character line, with `S` for size and `5` for content digest. All of them depend on the stored digests, and the digests are stored on the same machine. An attacker with root access can change both the file and the record, so these tools find accidents and unsophisticated changes, not a careful attacker. Packages also carry a signature, which `rpm -K` can check against an imported key and which apt checks through the repository, but that happens at install time.

## Why this part has no commands

The node containers of the playground are built from a minimal image, and they may not have `debsums` or the full package database tooling. More important, the Kubernetes binaries on a `kind` node are placed by the image build and were not installed by a package, so a package verification of the node would not cover them. A command that cannot cover the files you care about teaches the wrong lesson. On a node installed from the Kubernetes package repository the command applies, and you would run it against the `kubelet` package and look for lines that name `/usr/bin/kubelet`.

When a binary is not covered by any package record, the digest comparison of the file with a published digest is the only check, and you need an authenticated digest from the release.

## What to look for

On a real node, treat output from a verify command like this. An empty output means the files match the record. A line with a `5` on a binary in `/usr/bin` needs an explanation, because binaries do not change after install. A line on a file in `/etc` that is marked as configuration is normal when an operator edited it. Compare the finding with the change history of the node before you decide that an attacker is involved.

You can now say what the package manager checks and what it cannot see. The next signatures cover single files and images.

## Common pitfalls

> [!WARNING]
> - **Reading a clean result as proof of integrity.** The records live on the same machine as the files.
> - **Expecting package tools to cover manually placed binaries.** They only know files from packages.
> - **Treating every difference as an attack.** Edited configuration files are expected to differ.
> - **Running the check once.** Run it on a schedule, and keep the output as evidence.
