---
exam_objectives:
- Verify platform binaries before deploying
---
# Package Verification On A Node

A signature check happens at install time. Later, a file that a package installed can be changed on disk. This part explains how the package manager compares installed files with the package metadata, runs that check on a playground node, and shows which files the check cannot see.

## What the package manager remembers

When dpkg installs a Debian package, it records the list of files and, for many of them, an MD5 digest from the package. The command `dpkg --verify`, also written `dpkg -V`, compares the files on disk with that record and prints one line for each file that differs. Each line starts with nine characters. A `5` in the third place means that the content digest differs, and other positions mean a changed size, mode, owner or time. A question mark means that the check could not be done for that property. After the flags comes a letter `c` for configuration files, and then the path. A clean system prints nothing.

The tool `debsums` does a similar job with the digests stored in the package files. On RPM based systems the command `rpm -V` prints the same kind of nine character line, with `S` for size and `5` for content digest. All of them depend on the stored digests, and the digests are stored on the same machine. An attacker with root access can change both the file and the record, so these tools find accidents and unsophisticated changes, not a careful attacker. Packages also carry a signature, which `rpm -K` can check against an imported key and which apt checks through the repository, but that happens at install time.

## Run the check on a node

The playground node is a Debian-based container with `dpkg`, so the check runs there. Start with the file that matters most on a Kubernetes node. `dpkg -S` names the package that installed a path:

<!-- astrona:playground:renew -->

```sh
NODE=astro-ats-031-playground-050-03-control-plane
podman exec $NODE dpkg -S /usr/bin/kubelet
```

```text
dpkg-query: no path found matching pattern /usr/bin/kubelet
```

No package owns the `kubelet` here. The `kind` image build copied the Kubernetes binaries into place, so `dpkg` has no record of them, and a package check cannot cover them. On a node installed from the Kubernetes package repository, the `kubelet` package owns `/usr/bin/kubelet` and the check applies. For a binary without a package record, compare its digest with an authenticated digest from the release instead.

Files that did come from a package can be checked. The `base-files` package installs `/etc/issue` and other small files. Verify it:

```sh
podman exec $NODE dpkg --verify base-files
```

```text
missing     /usr/share/doc/base-files
missing     /usr/share/doc/base-files/README
missing     /usr/share/doc/base-files/README.FHS
missing     /usr/share/doc/base-files/changelog.gz
missing     /usr/share/doc/base-files/copyright
missing     /usr/share/lintian/overrides/base-files
missing     /usr/share/doc/base-files/FAQ
```

The `missing` lines are documentation files that the image build removed to save space. They are expected in a minimal image. Now change one installed file and verify again, this time without the `missing` lines:

```sh
podman exec $NODE sh -c 'echo changed >> /etc/issue'
podman exec $NODE sh -c 'dpkg --verify base-files | grep -v "^missing"'
```

```text
??5?????? c /etc/issue
```

The `5` in the third place says that the MD5 digest of `/etc/issue` no longer matches the package. The `c` marks a configuration file, which an administrator may edit on purpose. The same line without the `c` on a binary, such as `??5??????   /bin/mount`, needs an explanation, because binaries do not change after install. `dpkg --verify` in this version returns exit status 0 even when it prints a changed file, so a script must read the output, not the exit status.

## What to look for

On a real node, treat output from a verify command like this. An empty output means the files match the record. A line with a `5` on a binary in `/usr/bin` needs an explanation, because binaries do not change after install. A line on a file in `/etc` that is marked as configuration is normal when an operator edited it. Compare the finding with the change history of the node before you decide that an attacker is involved.

You can now say what the package manager checks and what it cannot see. The next signatures cover single files and images.

## Common pitfalls

> [!WARNING]
> - **Reading a clean result as proof of integrity.** The records live on the same machine as the files.
> - **Expecting package tools to cover manually placed binaries.** They only know files from packages.
> - **Treating every difference as an attack.** Edited configuration files are expected to differ.
> - **Running the check once.** Run it on a schedule, and keep the output as evidence.
> - **Testing the exit status of `dpkg --verify`.** It can be 0 while the output lists a changed file. Read the lines.
