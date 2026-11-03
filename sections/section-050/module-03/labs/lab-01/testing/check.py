#!/usr/bin/env python3
"""Grade one lab from live observations in the private environment."""
import json
import subprocess
import sys

CLUSTER = "ats-031-lab-050-03-01"
CONTEXT = "kind-astro-" + CLUSTER
CONTROL = "astro-%s-control-plane" % CLUSTER
WORKER = "astro-%s-worker" % CLUSTER


def run(*args, check=True):
    result = subprocess.run(args, capture_output=True, text=True, timeout=60)
    if check:
        assert result.returncode == 0, 'Required command failed: ' + ' '.join(args[:4])
    return result


def kubectl(*args):
    return run('kubectl', *args).stdout.strip()


def node(name, script, check=True):
    return run('podman', 'exec', name, 'sh', '-c', script, check=check)


def digest(name, path):
    return node(name, "sha256sum '%s' | cut -d' ' -f1" % path).stdout.strip()


def configmap(name, namespace='starfleet'):
    return json.loads(kubectl('-n', namespace, 'get', 'configmap', name, '-o', 'json')).get('data', {})
D = '/var/lib/training-release/signed/lab'


def main():
    assert kubectl('config', 'current-context') == CONTEXT, 'Refusing to operate on another Kubernetes context'
    gpg_ok = node(CONTROL, "cd %s && gpg --no-default-keyring --keyring ./publisher.gpg --verify gpg-notes.txt.asc gpg-notes.txt" % D, check=False).returncode == 0
    cosign_ok = node(CONTROL, "cd %s && cosign verify-blob --key cosign.pub --signature cosign-notes.txt.sig --insecure-ignore-tlog=true cosign-notes.txt" % D, check=False).returncode == 0
    assert gpg_ok != cosign_ok, 'Exactly one of the two signatures must fail; the staged files were changed or a tool is missing'
    forged = 'cosign' if gpg_ok else 'gpg'
    result = node(CONTROL, "cat %s/result.txt" % D, check=False)
    assert result.returncode == 0, 'Write the result file %s/result.txt on the control plane node' % D
    assert result.stdout.strip() == forged, 'The result file does not name the forged signature'
    print('Required result verified')


if __name__ == '__main__':
    try:
        main()
    except (AssertionError, KeyError, ValueError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
