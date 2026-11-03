#!/usr/bin/env python3
"""Grade one lab from live observations in the private environment."""
import json
import subprocess
import sys

CLUSTER = "ats-031-lab-050-02-02"
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
def kubelet_facts():
    pid = node(WORKER, "grep -l '^kubelet$' /proc/[0-9]*/comm | head -n 1 | cut -d/ -f3").stdout.strip()
    assert pid, 'The kubelet process was not found on the worker'
    path = node(WORKER, 'readlink /proc/%s/exe' % pid).stdout.strip()
    version = node(WORKER, '%s --version' % path).stdout.strip().split()[-1]
    return path, version, digest(WORKER, path)


def main():
    assert kubectl('config', 'current-context') == CONTEXT, 'Refusing to operate on another Kubernetes context'
    path, version, actual = kubelet_facts()
    data = configmap('kubelet-review')
    assert data.get('version') == version, 'Record the version that the worker kubelet reports'
    assert data.get('path') == path, 'Record the path of the running kubelet binary'
    assert data.get('sha256') == actual, 'Record the digest of the running kubelet binary'
    published = node(WORKER, "cat /var/lib/training-release/k8s/release/%s/bin/linux/*/kubelet.sha256" % version, check=False)
    assert published.returncode == 0, 'No staged checksum exists for this version'
    expected = 'match' if published.stdout.strip() == actual else 'mismatch'
    assert data.get('result') == expected, 'The result does not follow from comparing the digest with the staged checksum for this version'
    print('Required result verified')


if __name__ == '__main__':
    try:
        main()
    except (AssertionError, KeyError, ValueError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
