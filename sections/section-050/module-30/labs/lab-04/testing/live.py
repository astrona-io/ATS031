import re


def digest_of(reference):
    match = re.search(r'@sha256:([0-9a-f]{64})$', reference)
    return match.group(1) if match else None


deployment = get('deployment', 'relay')
pods = json.loads(kubectl('-n', NAMESPACE, 'get', 'pods', '-l', 'app=relay', '-o', 'json'))['items']
if wants('deployment-pinned'):
    image = deployment['spec']['template']['spec']['containers'][0]['image']
    pinned = digest_of(image)
    assert pinned, 'The relay Deployment image must be a reference with @sha256: and a 64 character digest'
    assert image.split('@')[0] in ('docker.io/library/python:3.13-alpine', 'library/python:3.13-alpine', 'python:3.13-alpine'), \
        'The image must be docker.io/library/python:3.13-alpine@sha256:<digest>'
    node = (pods[0]['spec'].get('nodeName') if pods else None) or WORKER
    listing = node_exec(node, 'ctr', '-n', 'k8s.io', 'images', 'ls').stdout.splitlines()
    started = [line.split()[2] for line in listing if line.split()[:1] == ['docker.io/library/python:3.13-alpine']]
    assert started and started[0] == 'sha256:' + pinned, 'Pin the digest of the image that the relay pod ran at the start'
    status = deployment['status']
    assert status.get('observedGeneration', 0) >= deployment['metadata']['generation'], 'Current generation has not been observed'
    assert all(status.get(field, 0) == 1 for field in ('replicas', 'updatedReplicas', 'readyReplicas')), 'The relay rollout is incomplete'
    assert len(pods) == 1, 'Exactly one relay pod must be running after the rollout'
    assert pods[0]['status']['containerStatuses'][0]['imageID'].endswith('sha256:' + pinned), 'The running imageID does not match the digest in the Deployment'
if wants('pin-review'):
    result = command(['kubectl', '-n', NAMESPACE, 'get', 'configmap', 'image-pin-review', '-o', 'json'], success=False)
    data = json.loads(result.stdout).get('data', {}) if result.returncode == 0 else {}
    assert len(pods) == 1, 'Exactly one relay pod must be running after the rollout'
    image_id = pods[0]['status']['containerStatuses'][0]['imageID']
    assert (data.get('imageID') or '').strip() == image_id, 'Record the imageID that the running relay pod reports in image-pin-review'
    assert (data.get('digest') or '').strip() == 'sha256:' + image_id.rsplit('sha256:', 1)[-1], 'Record the pinned digest (sha256:<digest>) in image-pin-review'
