release = '/var/lib/fleet-release'
signed = node_exec(NODE, 'openssl', 'dgst', '-sha256', '-verify', release + '/publisher.pub', '-signature',
                   release + '/SHA256SUMS.sig', release + '/SHA256SUMS', success=False).returncode == 0
assert signed, 'The signed manifest was changed; start the lab again'
trusted_digest = node_exec(NODE, 'cat', release + '/SHA256SUMS').stdout.split()[0]
genuine = [cache for cache in ('cache-1', 'cache-2', 'cache-3')
           if node_exec(NODE, 'sha256sum', f'/var/cache/fleet/{cache}/fleet-agent').stdout.split()[0] == trusted_digest]
assert len(genuine) == 1, 'The download caches were changed; start the lab again'


def stat(path):
    found = node_exec(NODE, 'stat', '-c', '%a %u %g', path, success=False)
    assert found.returncode == 0, path + ' does not exist'
    mode, owner, group = found.stdout.split()
    return int(mode, 8), int(owner), int(group)


def review():
    found = command(['kubectl', '-n', NAMESPACE, 'get', 'configmap', 'install-record', '-o', 'json'], success=False)
    assert found.returncode == 0, 'Create the ConfigMap install-record in ' + NAMESPACE
    return json.loads(found.stdout).get('data') or {}


if wants('installed-binary'):
    installed = '/opt/fleet/bin/fleet-agent'
    found = node_exec(NODE, 'sha256sum', installed, success=False)
    assert found.returncode == 0 and found.stdout.split()[0] == trusted_digest, 'The installed fleet-agent does not match the signed manifest'
    mode, owner, group = stat(installed)
    assert owner == 0 and group == 0, 'fleet-agent must be owned by root:root'
    assert mode & 0o777 == 0o755, 'fleet-agent must have mode 0755'
if wants('protected-directories'):
    for directory in ('/opt/fleet', '/opt/fleet/bin'):
        mode, owner, group = stat(directory)
        assert owner == 0, directory + ' must be owned by root'
        assert mode & 0o022 == 0, directory + ' must not be writable by group or others'
if wants('install-record'):
    data = review()
    assert data.get('cache', '').strip() == genuine[0], 'cache must name the cache that held the genuine fleet-agent'
    assert data.get('sha256', '').strip() == trusted_digest, 'sha256 must be the digest from the signed manifest'
