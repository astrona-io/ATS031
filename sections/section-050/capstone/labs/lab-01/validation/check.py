#!/usr/bin/env python3
"""Grade one lab from live observations in the private environment."""
import json
import subprocess
import sys

CLUSTER = "ats-031-capstone-050"
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
import re

B = '/var/lib/training-release/bundle'
A = '/var/lib/training-release/approved'


def main():
    assert kubectl('config', 'current-context') == CONTEXT, 'Refusing to operate on another Kubernetes context'
    assert node(CONTROL, "cd %s && openssl dgst -sha256 -verify publisher.pub -signature SHA256SUMS.sig SHA256SUMS" % B, check=False).returncode == 0, 'The bundle files were changed: the manifest signature no longer verifies'
    manifest = {}
    for line in node(CONTROL, 'cat %s/SHA256SUMS' % B).stdout.splitlines():
        value, name = line.split()
        manifest[name] = value
    genuine = sorted(n for n in ('kubectl', 'kubeadm') if digest(CONTROL, '%s/%s' % (B, n)) == manifest[n])
    rejected = sorted(n for n in ('kubectl', 'kubeadm') if n not in genuine)
    assert len(genuine) == 1, 'Exactly one bundle binary must fail verification'
    # Only verified binaries are deployed.
    listing = sorted(node(CONTROL, 'ls %s' % A).stdout.split())
    assert listing == genuine, 'The approved directory must hold exactly the verified binaries'
    for name in genuine:
        assert digest(CONTROL, '%s/%s' % (A, name)) == manifest[name], 'An approved binary does not match the manifest'
    # The running kubelet on the worker.
    pid = node(WORKER, "grep -l '^kubelet$' /proc/[0-9]*/comm | head -n 1 | cut -d/ -f3").stdout.strip()
    running = digest(WORKER, '/proc/%s/exe' % pid)
    assert running == manifest['kubelet'], 'The worker kubelet no longer matches the manifest'
    # The image is pinned and running.
    deployment = json.loads(kubectl('-n', 'starfleet', 'get', 'deployment', 'relay', '-o', 'json'))
    image = deployment['spec']['template']['spec']['containers'][0]['image']
    match = re.fullmatch(r'.*busybox.*@sha256:([0-9a-f]{64})', image)
    assert match, 'The relay image must name busybox and be pinned with @sha256:'
    wanted = match.group(1)
    status = deployment['status']
    assert status.get('observedGeneration', 0) >= deployment['metadata']['generation'], 'Current generation has not been observed'
    assert all(status.get(f, 0) == 1 for f in ('replicas', 'updatedReplicas', 'readyReplicas')), 'Deployment rollout is incomplete'
    pods = json.loads(kubectl('-n', 'starfleet', 'get', 'pods', '-l', 'app=relay', '-o', 'json'))['items']
    assert len(pods) == 1 and pods[0]['status']['containerStatuses'][0]['imageID'].endswith('sha256:' + wanted), 'The running imageID does not match the pinned digest'
    # The report.
    data = configmap('verification-report')
    expected = {
        'manifest_signature': 'verified',
        'genuine': ','.join(genuine),
        'rejected': ','.join(rejected),
        'kubelet': 'match',
        'kubelet_sha256': running,
        'image': image,
    }
    for key, value in expected.items():
        assert data.get(key) == value, 'verification-report field differs: ' + key
    print('Required result verified')


if __name__ == '__main__':
    try:
        main()
    except (AssertionError, KeyError, ValueError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
