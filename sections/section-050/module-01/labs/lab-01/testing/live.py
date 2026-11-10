release = '/var/lib/training-release'
node_exec(NODE, 'openssl', 'dgst', '-sha256', '-verify', release + '/publisher.pub', '-signature', release + '/checksums.sig', release + '/checksums.txt')
trusted = node_exec(NODE, 'cat', release + '/checksums.txt').stdout.split()[0]
actual = node_exec(NODE, 'sha256sum', release + '/kubectl').stdout.split()[0]
changed = node_exec(NODE, 'sha256sum', release + '/kubectl-tampered').stdout.split()[0]
assert trusted == actual and changed != trusted, 'The staged release files were changed'


def review():
    found = command(['kubectl', '-n', NAMESPACE, 'get', 'configmap', 'artifact-review', '-o', 'json'], success=False)
    assert found.returncode == 0, 'Record the ConfigMap artifact-review in ' + NAMESPACE
    return json.loads(found.stdout).get('data') or {}


if wants('review-verdict'):
    data = review()
    assert data.get('result') == 'verified', 'artifact-review must record result verified'
    assert data.get('tampered') == 'rejected', 'artifact-review must record tampered rejected'
if wants('review-digest'):
    assert review().get('sha256') == trusted, 'Bind the review to the verified sha256 digest'
