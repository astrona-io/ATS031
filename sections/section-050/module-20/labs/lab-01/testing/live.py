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


def recorded_path():
    return pick().get('path', '').strip().removeprefix(mirror + '/').lstrip('/')


if wants('stable-version'):
    parts = recorded_path().split('/')
    assert len(parts) > 1 and parts[0] == 'release', 'path must start with release/<version>/'
    assert parts[1] == stable, 'The version in path must be the current stable version from release/stable.txt'
if wants('release-path'):
    path = recorded_path()
    assert path == expected_path, 'path must be release/<stable version>/bin/linux/<worker architecture>/kubeadm'
if wants('release-digest'):
    assert pick().get('sha256', '').strip() == published, 'sha256 must be the published digest of that kubeadm file'
