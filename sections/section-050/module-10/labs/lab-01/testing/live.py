import re

release = '/var/lib/fleet-release'
names = ['fleet-agent', 'fleet-cli', 'fleet-proxy', 'fleet-sync', 'fleet-scan', 'fleet-init']
listed = {}
for line in node_exec(NODE, 'cat', release + '/SHA256SUMS').stdout.splitlines():
    digest, name = line.split(None, 1)
    listed[name.strip()] = digest
assert sorted(listed) == sorted(names), 'SHA256SUMS was changed; start the lab again'
staged = node_exec(NODE, 'cat', '/var/lib/astrona-lab/050-01-01-staged', success=False)
assert staged.returncode == 0, 'The record of the staged files is missing; start the lab again'
assert node_exec(NODE, 'sh', '-c', 'cd /var/lib/fleet-release && sha256sum --check --quiet /var/lib/astrona-lab/050-01-01-staged', success=False).returncode == 0, \
    'The files or SHA256SUMS were changed; start the lab again'
current = {}
for line in node_exec(NODE, 'sha256sum', *[release + '/' + name for name in names]).stdout.splitlines():
    digest, path = line.split(None, 1)
    current[path.strip().rsplit('/', 1)[1]] = digest
failed = {name for name in names if current[name] != listed[name]}
assert failed, 'Every file matches the manifest again; start the lab again'


def record():
    found = command(['kubectl', '-n', NAMESPACE, 'get', 'configmap', 'manifest-check', '-o', 'json'], success=False)
    assert found.returncode == 0, 'Create the ConfigMap manifest-check in ' + NAMESPACE
    return json.loads(found.stdout).get('data') or {}


if wants('failed-files'):
    named = set(re.split(r'[\s,]+', record().get('failed', '').strip())) - {''}
    assert named == failed, 'failed must list every file that fails the manifest, and no other file'
if wants('agent-digest'):
    assert record().get('agent-sha256', '').strip() == current['fleet-agent'], 'agent-sha256 must be the current SHA-256 digest of fleet-agent'
