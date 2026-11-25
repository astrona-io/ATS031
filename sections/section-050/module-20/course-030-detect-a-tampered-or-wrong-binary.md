# Detect A Tampered Or Wrong Binary

A `FAILED` result has several possible causes, and each cause needs a different response. Someone may have changed the bytes. The file may be for another architecture or another version. Or the checksum file may belong to another release.

On this page, you check four suspicious downloads. Then, for each one, you find out what its bytes really are.

## Check every download

The downloads directory of the mirror holds a `kubectl`, a `kubeadm`, a `kubelet` and two more copies of `kubectl`. Each file has a checksum file with its name plus the suffix `.sha256`. List the directory, then check every file against its own checksum file:

<!-- astrona:playground:renew -->

```sh
NODE=astro-ats-031-playground-050-02-control-plane
MIRROR=/var/lib/training-release/k8s
podman exec $NODE ls $MIRROR/downloads
podman exec -w $MIRROR/downloads $NODE sh -c 'for f in $(ls | grep -v "\.sha256$"); do if echo "$(cat $f.sha256)  $f" | sha256sum --check --status; then echo "$f: OK"; else echo "$f: FAILED"; fi; done'
```

One file passes: `kubectl`. The other four fail:

- `kubeadm`;
- `kubelet`;
- a copy of `kubectl` named for the other architecture;
- a copy of `kubectl` named for the older version.

The four failures have four different causes, and the digest alone does not tell them apart.

![Diagram: the five downloads, what their bytes are, which checksum file came with each, and the result; only kubectl passes](images/downloads-and-checksums.svg)

The drawing lists each download with what its bytes really are and which release its checksum file came from. The rest of this page shows how you find out the middle column yourself.

## Find out what the bytes are

The release tree of the mirror holds the digests of every staged file. So compute the digest of a failing file, and search the tree for it. If the digest appears in a `.sha256` file, the bytes are exactly that published file. If it appears nowhere, the bytes are not any file in the release.

```sh
podman exec -w $MIRROR/downloads $NODE sh -c 'for f in kubeadm kubelet; do echo "== $f"; grep -rl "$(sha256sum $f | cut -d" " -f1)" ../release || echo "no published file has these bytes"; done'
```

For `kubeadm`, the search finds nothing. No published file has these bytes. The checksum file for `kubeadm` is the genuine one, so someone changed the bytes after the project published the digest. This is the tampered case: the file has the right name and the wrong content. Do not run it.

For `kubelet`, the search finds a `.sha256` file in the newer release directory. So the bytes are the genuine `kubelet` of that release. The checksum file that came with the download belongs to the older release. That means the checksum file is stale, and the binary is fine. The fix is to fetch the checksum file again from the directory of the same version, not to throw away the binary.

Now run the same search for the two `kubectl` copies:

```sh
podman exec -w $MIRROR/downloads $NODE sh -c 'for f in $(ls | grep "^kubectl-"  | grep -v "\.sha256$"); do echo "== $f"; grep -rl "$(sha256sum $f | cut -d" " -f1)" ../release; done'
```

The file named for the other architecture matches the `kubectl.sha256` in the directory of the other architecture. So it is a genuine file for the wrong processor, paired with the checksum file for this processor. The file named for the older version matches the checksum file of the newer version. So its name makes a false claim about its version.

![Diagram: a failed check leads to a search of the release tree for the digest, and the match decides one of four actions: reject changed bytes, fetch the right file for a wrong platform or a wrong version, or fetch the checksum file again when it is stale](images/failed-check-causes.svg)

The drawing shows one failed check leading to four different actions, depending on which published file the bytes match.

The search works here because the mirror holds the digests of other files. On the real site, you use the same idea: you fetch the checksum file for the other architecture or version that you suspect. A tampered file cannot be explained that way, and that is the signal to reject it.

## What a failure does not tell you

A mismatch shows that these bytes differ from the published digest. It does not show who changed them or when. And a match does not show that the digest itself is trustworthy.

Treat a tampered download as a security event. Keep the file for review, do not run it, and report where it came from.

You can now sort a failing download into one of four causes. The open question is the version that a binary prints about itself, which is another claim you can test.

## Common pitfalls

> [!WARNING]
> - **Treating every mismatch as an attack.** A wrong architecture or a stale checksum file is a download mistake, and the fix is different.
> - **Treating every mismatch as a mistake.** If the digest matches no published file, reject the file.
> - **Replacing the checksum file with one computed from the download.** That check always passes and proves nothing.
> - **Running a failing binary to find out what it is.** Search with digests instead.
