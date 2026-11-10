def worker_shell(script, success=True):
    return node_exec(WORKER, 'sh', '-c', script, success=success)


def review():
    """The kubelet-review ConfigMap's data, or {} while it does not exist."""
    result = command(['kubectl', '-n', NAMESPACE, 'get', 'configmap', 'kubelet-review', '-o', 'json'], success=False)
    return json.loads(result.stdout).get('data', {}) if result.returncode == 0 else {}


pid = worker_shell("grep -l '^kubelet$' /proc/[0-9]*/comm | head -n 1 | cut -d/ -f3").stdout.strip()
assert pid, 'The kubelet process was not found on the worker'
path = worker_shell('readlink /proc/%s/exe' % pid).stdout.strip()
version = worker_shell('%s --version' % path).stdout.strip().split()[-1]
actual = worker_shell("sha256sum '%s' | cut -d' ' -f1" % path).stdout.strip()
data = review()
if wants('kubelet-binary'):
    assert data.get('version') == version, 'Record the version that the worker kubelet reports in kubelet-review'
    assert data.get('path') == path, 'Record the path of the running kubelet binary in kubelet-review'
if wants('kubelet-digest'):
    assert data.get('sha256') == actual, 'Record the digest of the running kubelet binary in kubelet-review'
if wants('checksum-result'):
    published = worker_shell('cat /var/lib/training-release/k8s/release/%s/bin/linux/*/kubelet.sha256' % version, success=False)
    assert published.returncode == 0, 'No staged checksum exists for this version'
    expected = 'match' if published.stdout.strip() == actual else 'mismatch'
    assert data.get('result') == expected, 'The result in kubelet-review does not follow from comparing the digest with the staged checksum for this version'
