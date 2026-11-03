---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Summary

Release binaries are published at addresses built from the version, the operating system and the CPU architecture. Each binary has a checksum file next to it, and the file holds only the digest. A file in the wrong directory, from another architecture or another version, produces a digest that does not match even though nothing was attacked.

`sha256sum --check` reads lines made of a digest, two spaces and a file name. The published checksum file has no name, so the line is built by hand. A line with one space, or a missing file, is an error of a different kind from a mismatch, and a script must read the exit status and use `--strict` so a malformed line cannot pass.

When a check fails, the digest of the failing file identifies what the bytes are. Bytes that match no published file were changed. Bytes that match another architecture or version are a download mistake. Genuine bytes with a checksum file from another release show that the checksum file is stale. Each cause has a different action, and a changed file is rejected and never run.

A binary reports its own version, source commit, build date and platform. These values catch download mistakes and show compatibility with the cluster, but a changed binary can print any version, so the digest decides.

On a node, the file that runs is found through the process, by following `/proc/<pid>/exe`, and the digest of that file is compared with the published digest for the version that the binary reports. This shows the bytes of the running program at that moment. It cannot give strong evidence on a node that an attacker controls, because the tools on the node can be replaced.

Key facts to remember:

- The release address is made of version, operating system and architecture.
- The line format is digest, two spaces and file name.
- A search for the failing digest tells tampering from a download mistake.
- The version output is a claim; the digest is the check.
- Hash `/proc/<pid>/exe` to check what runs.

<!-- astrona:playground:destroy -->
