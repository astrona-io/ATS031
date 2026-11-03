---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# sha256sum And The Check Format

The command that the exam expects is short, and it fails in quiet ways when its input has the wrong shape. This part verifies a binary with `sha256sum --check`, explains the line format that the tool reads, and shows what the exit status tells a script.

## Compute a digest and compare it

`sha256sum` reads a file and prints its SHA-256 digest followed by the file name. You could compare that digest with the published one by eye, but a person misses a changed character in 64 digits. The `--check` option makes the tool do the comparison. It reads lines of the form `digest`, two spaces, `file name`, recomputes the digest of each named file and reports `OK` or `FAILED`.

The published `.sha256` file holds only the digest, so you add the two spaces and the name yourself. The downloads directory of the mirror holds a `kubectl` and its checksum file:

<!-- astrona:playground:renew -->

```sh
NODE=astro-ats-031-playground-050-02-control-plane
MIRROR=/var/lib/training-release/k8s
podman exec -w $MIRROR/downloads $NODE sh -c 'echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check'
echo "exit status: $?"
```

The command inside `sh -c` builds the line `digest`, two spaces, `kubectl` and pipes it to `sha256sum --check`. The tool prints `kubectl: OK`. The exit status of `podman exec` is the exit status of the command inside, which is 0 here. The option `-w` sets the working directory inside the node container, so `kubectl` is found by its short name.

## What the tool reads

The format is strict. The digest and the name are separated by two characters: a space and then either a second space for text mode or an asterisk for binary mode. Linux treats both the same. The file name is taken as it is written, so it is looked up relative to the current directory.

Three input mistakes are common. The first is to give `sha256sum --check` the published file directly, because that file has no file name on its line:

```sh
podman exec -w $MIRROR/downloads $NODE sha256sum --check kubectl.sha256
echo "exit status: $?"
```

The tool reports that no lines were properly formatted, checks nothing and returns a nonzero status. The exact wording differs between versions of the tool, so read the message and the status together. The second mistake is one space instead of two:

```sh
podman exec -w $MIRROR/downloads $NODE sh -c 'echo "$(cat kubectl.sha256) kubectl" | sha256sum --check'
echo "exit status: $?"
```

This also fails with an improperly formatted line and a nonzero status. The third mistake is to run the check in a directory where the named file does not exist. The tool then reports that it could not open the file, which is a failure of a different kind from a digest mismatch.

## Exit status in scripts

A script must not read the printed text. It reads the exit status. The status is 0 only when every line was formatted and every file matched. Add `--status` to print nothing and use the status alone, and add `--strict` to make improperly formatted lines an error even when other lines were fine.

```sh
podman exec -w $MIRROR/downloads $NODE sh -c 'echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check --status --strict' && echo "verified" || echo "not verified"
```

The result is `verified`. A pipeline that deploys the binary only when this command succeeds cannot be fooled by a log line that nobody read. The reverse is also true: a script that ignores the status installs the file whatever the check said.

You can now check a binary against its published digest and read the result as a status. The next question is what to do when the answer is `FAILED`.

## Common pitfalls

> [!WARNING]
> - **Writing one space instead of two.** The line is improperly formatted and nothing is compared.
> - **Passing the `.sha256` file to `--check`.** It has no file name on its line.
> - **Reading only the printed text.** Test the exit status, and use `--strict` so a malformed line cannot pass.
> - **Checking in the wrong directory.** A missing file is an error, not a mismatch.
