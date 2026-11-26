bundle = '/var/lib/node-bundle'
binaries = ('kube-apiserver', 'kube-controller-manager', 'kube-scheduler', 'kube-proxy', 'kubectl', 'kubeadm', 'kubelet')
failing = [binary for binary in binaries
           if node_exec(NODE, 'cat', f'{bundle}/{binary}.sha256').stdout.strip()
           != node_exec(NODE, 'sha256sum', f'{bundle}/{binary}').stdout.split()[0]]
assert len(failing) == 1, 'The staged files were changed: exactly one binary must fail verification; start the lab again'

def recorded_name():
    found = command(['kubectl', '-n', NAMESPACE, 'get', 'configmap', 'failing-binary', '-o', 'json'], success=False)
    assert found.returncode == 0, 'Create the ConfigMap failing-binary in ' + NAMESPACE
    data = json.loads(found.stdout).get('data') or {}
    assert data.get('name', '').strip(), 'The ConfigMap failing-binary needs the key name'
    return data['name'].strip()


if wants('failing-record'):
    recorded_name()
if wants('binary-name'):
    assert recorded_name() in binaries, \
        'name must be the bare file name of one staged binary, without a directory or the .sha256 suffix'
if wants('failing-binary'):
    assert recorded_name() == failing[0], 'name must be the one binary that fails verification'
