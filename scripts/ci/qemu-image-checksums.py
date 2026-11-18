#!/usr/bin/env python3
"""Keep the checksums of the QEMU images in config.yaml files current.

A qemu playground or lab names its image as an OCI tag with an {ARCH}
placeholder and pins one checksum per architecture:

    source: ghcr.io/astrona-io/ubuntu-qcow2-image:24.04-cks-20261118-{ARCH}
    checksums:
      amd64: sha256:...
      arm64: sha256:...

astrona checks the checksum against the digest of the single image.qcow2
layer of the tag. Renovate bumps the date in the tag but cannot compute that
digest, so this script reads it from the registry (anonymous pull, the
images are public) and writes it.

    python3 scripts/ci/qemu-image-checksums.py           # rewrite stale checksums
    python3 scripts/ci/qemu-image-checksums.py --check   # fail when one is stale
"""
import json
from pathlib import Path
import re
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
SOURCE = re.compile(r'^(?P<indent> *)source: (?P<registry>[^/\s]+)/(?P<repository>[^:\s]+):(?P<tag>\S*\{ARCH\}\S*)\n'
                    r'(?P=indent)checksums:\n(?P<checksums>(?:(?P=indent)  \w+: sha256:[0-9a-f]{64}\n)+)', re.M)
CHECKSUM = re.compile(r'^(?P<indent> *)(?P<arch>\w+): (?P<digest>sha256:[0-9a-f]{64})$', re.M)
MANIFEST_TYPES = 'application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json'
DIGESTS = {}


def get_json(url, headers=None):
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}), timeout=30) as response:
        return json.load(response)


def image_digest(registry, repository, tag):
    """The digest of the image.qcow2 layer of one tag."""
    key = (registry, repository, tag)
    if key not in DIGESTS:
        token = get_json(f'https://{registry}/token?scope=repository:{repository}:pull')['token']
        manifest = get_json(f'https://{registry}/v2/{repository}/manifests/{tag}',
                            {'Authorization': f'Bearer {token}', 'Accept': MANIFEST_TYPES})
        layers = manifest['layers']
        named = [layer for layer in layers if layer.get('annotations', {}).get('org.opencontainers.image.title') == 'image.qcow2']
        if len(named) != 1 and len(layers) != 1:
            raise SystemExit(f'{registry}/{repository}:{tag}: expected one image.qcow2 layer')
        DIGESTS[key] = (named or layers)[0]['digest']
    return DIGESTS[key]


def update(text):
    """The text with current checksums, and the list of changes."""
    changes = []

    def checksums(match):
        def one(line):
            tag = match['tag'].replace('{ARCH}', line['arch'])
            digest = image_digest(match['registry'], match['repository'], tag)
            if digest != line['digest']:
                changes.append(f'{tag}: {line["digest"]} -> {digest}')
            return f'{line["indent"]}{line["arch"]}: {digest}'
        return match[0].replace(match['checksums'], CHECKSUM.sub(one, match['checksums']))

    return SOURCE.sub(checksums, text), changes


def main(arguments):
    check = '--check' in arguments
    stale = False
    for path in sorted(ROOT.glob('sections/**/config.yaml')):
        text = path.read_text()
        if '{ARCH}' not in text:
            continue
        new, changes = update(text)
        for change in changes:
            print(f'{path.relative_to(ROOT)}: {change}')
        if changes:
            stale = True
            if not check:
                path.write_text(new)
    if check and stale:
        sys.exit('FAIL: stale QEMU image checksums; run python3 scripts/ci/qemu-image-checksums.py')
    print('Updated the stale QEMU image checksums' if stale else 'PASS: QEMU image checksums match the registry')


if __name__ == '__main__':
    main(sys.argv[1:])
