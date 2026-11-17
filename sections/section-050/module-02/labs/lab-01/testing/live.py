mirror = '/var/lib/k8s-mirror'
stable = node_exec(NODE, 'cat', mirror + '/release/stable.txt').stdout.strip()
assert stable in ('v1.33.7', 'v1.34.3', 'v1.35.1'), 'stable.txt was changed; start the lab again'
machine = node_exec(WORKER, 'uname', '-m').stdout.strip()
architecture = {'x86_64': 'amd64', 'aarch64': 'arm64'}[machine]
expected_path = f'release/{stable}/bin/linux/{architecture}/kubeadm'
published = node_exec(NODE, 'cat', f'{mirror}/{expected_path}.sha256').stdout.strip()


def pick():
    found = command(['kubectl', '-n', NAMESPACE, 'get', 'configmap', 'release-pick', '-o', 'json'], success=False)
    assert found.returncode == 0, 'Create the ConfigMap release-pick in ' + NAMESPACE
    return json.loads(found.stdout).get('data') or {}


if wants('release-path'):
    path = pick().get('path', '').strip().removeprefix(mirror + '/').lstrip('/')
    assert path == expected_path, 'path must be release/<stable version>/bin/linux/<worker architecture>/kubeadm'
if wants('release-digest'):
    assert pick().get('sha256', '').strip() == published, 'sha256 must be the published digest of that kubeadm file'
