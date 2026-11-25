release = '/var/lib/relay-release'
trusted = []
for mirror in ('a', 'b', 'c'):
    folder = f'{release}/mirror-{mirror}'
    signed = node_exec(NODE, 'openssl', 'dgst', '-sha256', '-verify', release + '/publisher.pub',
                       '-signature', folder + '/SHA256SUMS.sig', folder + '/SHA256SUMS', success=False).returncode == 0
    matches = node_exec(NODE, 'sh', '-c', f'cd {folder} && sha256sum --check --status --strict SHA256SUMS',
                        success=False).returncode == 0
    if signed and matches:
        trusted.append(mirror)
assert len(trusted) == 1, 'The staged mirrors were changed; start the lab again'
trusted_mirror = trusted[0]
trusted_digest = node_exec(NODE, 'cat', f'{release}/mirror-{trusted_mirror}/SHA256SUMS').stdout.split()[0]


def review():
    found = command(['kubectl', '-n', NAMESPACE, 'get', 'configmap', 'artifact-review', '-o', 'json'], success=False)
    assert found.returncode == 0, 'Create the ConfigMap artifact-review in ' + NAMESPACE
    return json.loads(found.stdout).get('data') or {}


if wants('trusted-mirror'):
    named = review().get('mirror', '').strip().removeprefix('mirror-')
    assert named == trusted_mirror, 'mirror must name the one mirror whose manifest has a good publisher signature and matches its binary'
if wants('review-digest'):
    assert review().get('sha256', '').strip() == trusted_digest, 'sha256 must be the relay-agent digest from the authenticated manifest'
