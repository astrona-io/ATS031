index = '/var/lib/release-index/release'
incoming = '/var/lib/k8s-incoming'
architecture = {'x86_64': 'amd64', 'aarch64': 'arm64'}[node_exec(NODE, 'uname', '-m').stdout.strip()]
other = 'arm64' if architecture == 'amd64' else 'amd64'


def published(version, arch):
    return node_exec(NODE, 'cat', f'{index}/{version}/bin/linux/{arch}/kubectl.sha256').stdout.strip()


expected = published('v1.35.0', architecture)
causes = {}
for number in range(1, 6):
    batch = f'batch-{number}'
    actual = node_exec(NODE, 'sha256sum', f'{incoming}/{batch}/kubectl').stdout.split()[0]
    shipped = node_exec(NODE, 'cat', f'{incoming}/{batch}/kubectl.sha256').stdout.strip()
    if actual == expected:
        causes[batch] = 'ok' if shipped == expected else 'stale-checksum'
    elif actual == published('v1.35.0', other):
        causes[batch] = 'wrong-arch'
    elif actual == published('v1.34.4', architecture):
        causes[batch] = 'wrong-version'
    else:
        causes[batch] = 'tampered'
assert sorted(causes.values()) == sorted(['ok', 'stale-checksum', 'wrong-arch', 'wrong-version', 'tampered']), \
    'The staged batches were changed; start the lab again'


def triage():
    found = command(['kubectl', '-n', NAMESPACE, 'get', 'configmap', 'download-triage', '-o', 'json'], success=False)
    assert found.returncode == 0, 'Create the ConfigMap download-triage in ' + NAMESPACE
    return json.loads(found.stdout).get('data') or {}


if wants('rejected-download'):
    tampered = [batch for batch, cause in causes.items() if cause == 'tampered'][0]
    assert triage().get('rejected', '').strip() == tampered, 'rejected must name the batch whose kubectl matches no published digest'
if wants('checksum-causes'):
    data = triage()
    for batch, cause in causes.items():
        if cause in ('ok', 'stale-checksum'):
            assert data.get(batch, '').strip() == cause, f'{batch} has the wrong cause'
if wants('failure-causes'):
    data = triage()
    for batch, cause in causes.items():
        if cause in ('wrong-arch', 'wrong-version', 'tampered'):
            assert data.get(batch, '').strip() == cause, f'{batch} has the wrong cause'
