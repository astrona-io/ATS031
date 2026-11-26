import re

downloads = '/var/lib/k8s-downloads'
tools = ('kubectl', 'kubeadm', 'kubelet')
published = {tool: node_exec(NODE, 'cat', f'{downloads}/{tool}.sha256').stdout.strip() for tool in tools}
actual = {tool: node_exec(NODE, 'sha256sum', f'{downloads}/{tool}').stdout.split()[0] for tool in tools}
failing = [tool for tool in tools if published[tool] != actual[tool]]
assert len(failing) <= 1, 'The downloads were changed; start the lab again'
staged = node_exec(NODE, 'cat', '/var/lib/astrona-lab/050-02-02-staged', success=False)
assert staged.returncode == 0, 'The record of the staged files is missing; start the lab again'
assert node_exec(NODE, 'sh', '-c', 'cd /var/lib/k8s-downloads && sha256sum --check --quiet /var/lib/astrona-lab/050-02-02-staged', success=False).returncode == 0, \
    'The downloads or their .sha256 files were changed; start the lab again'

if wants('check-file'):
    found = node_exec(NODE, 'cat', downloads + '/SHA256SUMS', success=False)
    assert found.returncode == 0, 'Create ' + downloads + '/SHA256SUMS'
    listed = {}
    for line in found.stdout.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r'([0-9a-f]{64})  (\S+)', line.rstrip('\r'))
        assert match, 'Each line must be <64 hex digits><two spaces><file name>: ' + line
        listed[match.group(2)] = match.group(1)
    assert set(listed) == set(tools), 'SHA256SUMS must list exactly kubectl, kubeadm and kubelet by file name only'
    for tool in tools:
        assert listed[tool] == published[tool], f'The digest for {tool} must come from {tool}.sha256'
def result():
    found = command(['kubectl', '-n', NAMESPACE, 'get', 'configmap', 'download-check', '-o', 'json'], success=False)
    assert found.returncode == 0, 'Create the ConfigMap download-check in ' + NAMESPACE
    return json.loads(found.stdout).get('data') or {}


if wants('check-result'):
    assert result().get('exit-status', '').strip() == ('1' if failing else '0'), 'exit-status must be the exit status of the strict check'
if wants('failed-download'):
    assert result().get('failed', '').strip() == (failing[0] if failing else 'none'), 'failed must name the failing download, or be none'
