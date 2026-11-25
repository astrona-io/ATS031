release = '/var/lib/kubelet-release'
architecture = {'x86_64': 'amd64', 'aarch64': 'arm64'}[node_exec(WORKER, 'uname', '-m').stdout.strip()]
pids = node_exec(WORKER, 'pidof', 'kubelet').stdout.split()
assert len(pids) == 1, 'Exactly one kubelet process must run on the worker node'
running_path = node_exec(WORKER, 'readlink', f'/proc/{pids[0]}/exe').stdout.strip()
running_digest = node_exec(WORKER, 'sha256sum', f'/proc/{pids[0]}/exe').stdout.split()[0]
dropin = node_exec(WORKER, 'cat', '/etc/systemd/system/kubelet.service.d/20-node-agent.conf', success=False).stdout
assert running_path != '/usr/bin/kubelet' and ('ExecStart=' + running_path + ' ') in dropin, \
    'Do not restart the kubelet or change its files; start the lab again'
published = node_exec(WORKER, 'cat', f'{release}/v1.35.0/bin/linux/{architecture}/kubelet.sha256').stdout.strip()
version = get('node', WORKER, namespace=None)['status']['nodeInfo']['kubeletVersion']
expected_result = 'match' if running_digest == published else 'mismatch'


def review():
    found = command(['kubectl', '-n', NAMESPACE, 'get', 'configmap', 'kubelet-review', '-o', 'json'], success=False)
    assert found.returncode == 0, 'Create the ConfigMap kubelet-review in ' + NAMESPACE
    return json.loads(found.stdout).get('data') or {}


if wants('kubelet-binary'):
    data = review()
    assert data.get('version', '').strip() == version, 'version must be the version that the running kubelet reports, for example ' + 'v1.35.0'
    assert data.get('path', '').strip() == running_path, 'path must be the binary of the running kubelet process'
if wants('kubelet-digest'):
    assert review().get('sha256', '').strip() == running_digest, 'sha256 must be the digest of the running kubelet binary'
if wants('checksum-result'):
    assert review().get('result', '').strip() == expected_result, 'result must say whether the running kubelet matches the published digest'
