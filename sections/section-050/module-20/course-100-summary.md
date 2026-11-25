# Summary

The Kubernetes project publishes its release binaries at addresses built from three facts: the version, the operating system and the CPU architecture. Each binary has a checksum file next to it, with the suffix `.sha256`, and that file holds only the digest. A file from the wrong directory, for another architecture or another version, has a digest that does not match, even though nobody attacked it.

`sha256sum --check` reads lines made of a digest, two spaces and a file name. The published checksum file has no name in it, so you build the line yourself. A line with one space, or a file that is missing, is a different kind of error from a mismatch. A script must read the exit status, not the printed text, and should use `--strict` so that a malformed line cannot pass.

When a check fails, the digest of the failing file tells you what the bytes are. Bytes that match no published file were changed. Bytes that match another architecture or another version show a download mistake. Genuine bytes that came with a checksum file from another release show that the checksum file is stale. Each cause needs a different action, and you reject a changed file and never run it.

A binary reports its own version, source commit, build date and platform. These values catch download mistakes and show whether the binary fits the version of the cluster. But a changed binary can print any version, so the digest decides.

On a node, you find the file that runs through the process, by following `/proc/<pid>/exe`. You compare the digest of that file with the published digest for the version that the binary reports. This check shows the bytes of the running program at that moment. It cannot give strong evidence on a node that an attacker controls, because the attacker can replace the tools on the node too.

Key facts to remember:

- The release address is made of the version, the operating system and the architecture.
- The check line format is digest, two spaces and file name.
- A search for the failing digest tells tampering apart from a download mistake.
- The version output is a claim; the digest is the check.
- Hash `/proc/<pid>/exe` to check what runs.

<!-- astrona:playground:destroy -->
