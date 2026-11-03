#!/usr/bin/env python3
"""Grade one lab from live observations in the private environment."""
import json
import subprocess
import sys

CLUSTER = "ats-031-lab-050-03-02"
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


def pinned_digest(image):
    match = re.search(r'@sha256:([0-9a-f]{64})$', image)
    assert match, 'The Deployment image must be a reference with @sha256: and a 64 character digest'
    return match.group(1)


def main():
    assert kubectl('config', 'current-context') == CONTEXT, 'Refusing to operate on another Kubernetes context'
    deployment = json.loads(kubectl('-n', 'starfleet', 'get', 'deployment', 'relay', '-o', 'json'))
    image = deployment['spec']['template']['spec']['containers'][0]['image']
    wanted = pinned_digest(image)
    assert image.split('@')[0].endswith('busybox'), 'Keep the busybox image repository'
    status = deployment['status']
    assert status.get('observedGeneration', 0) >= deployment['metadata']['generation'], 'Current generation has not been observed'
    assert all(status.get(f, 0) == 1 for f in ('replicas', 'updatedReplicas', 'readyReplicas')), 'Deployment rollout is incomplete'
    pods = json.loads(kubectl('-n', 'starfleet', 'get', 'pods', '-l', 'app=relay', '-o', 'json'))['items']
    assert len(pods) == 1, 'Exactly one relay pod must be running after the rollout'
    image_id = pods[0]['status']['containerStatuses'][0]['imageID']
    assert image_id.endswith('sha256:' + wanted), 'The running imageID does not match the digest in the Deployment'
    data = configmap('image-pin-review')
    assert data.get('digest') == 'sha256:' + wanted, 'Record the pinned digest in image-pin-review'
    assert data.get('imageID') == image_id, 'Record the imageID that the running pod reports'
    print('Required result verified')


if __name__ == '__main__':
    try:
        main()
    except (AssertionError, KeyError, ValueError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
