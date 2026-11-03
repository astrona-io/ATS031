#!/usr/bin/env python3
"""Grade one lab from live observations in the private environment."""
import json
import subprocess
import sys

CLUSTER = "ats-031-lab-050-02-01"
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
R = '/var/lib/training-release/k8s/lab'


def main():
    assert kubectl('config', 'current-context') == CONTEXT, 'Refusing to operate on another Kubernetes context'
    failing = []
    for tool in ('kubectl', 'kubeadm', 'kubelet'):
        expected = node(CONTROL, "cat %s/%s.sha256" % (R, tool)).stdout.strip()
        actual = digest(CONTROL, '%s/%s' % (R, tool))
        if expected != actual:
            failing.append(tool)
    assert len(failing) == 1, 'The staged files were changed: exactly one binary must fail verification'
    result = node(CONTROL, "cat %s/result.txt" % R, check=False)
    assert result.returncode == 0, 'Write the result file %s/result.txt on the control plane node' % R
    assert result.stdout.strip() == failing[0], 'The result file does not name the binary that fails verification'
    print('Required result verified')


if __name__ == '__main__':
    try:
        main()
    except (AssertionError, KeyError, ValueError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
