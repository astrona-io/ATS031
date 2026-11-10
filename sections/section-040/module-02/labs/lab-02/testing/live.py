def http_status(namespace, pod, url):
    """HTTP status from a client pod, or denied when the request cannot connect."""
    try:
        result = subprocess.run(['kubectl', '-n', namespace, 'exec', pod, '--', 'curl', '-sk', '-m', '3', '-o', '/dev/null', '-w', '%{http_code}', url], capture_output=True, text=True, timeout=25)
    except subprocess.TimeoutExpired:
        return 'denied'
    if result.returncode != 0 and result.stdout.strip() in ('', '000'):
        return 'denied'
    return result.stdout.strip()


def expect_http(namespace, pod, url, expected, label):
    actual = http_status(namespace, pod, url)
    assert actual == expected, '%s: request from %s/%s to %s gave %s, expected %s' % (label, namespace, pod, url, actual, expected)


METADATA = 'http://169.254.169.254/latest/meta-data/'
labels = get('pod', 'agent')['metadata'].get('labels', {})
assert labels.get('role') == 'cloud-agent', 'Pod %s/agent must keep label role=cloud-agent' % NAMESPACE
assert 'role' not in get('pod', 'shuttle')['metadata'].get('labels', {}), 'Pod %s/shuttle must not have label role' % NAMESPACE
expect_http(NAMESPACE, 'agent', METADATA, '200', 'agent must reach the metadata address')
expect_http(NAMESPACE, 'shuttle', 'http://probe/', '200', 'shuttle must reach the probe Service')
expect_http(NAMESPACE, 'agent', 'http://probe/', '200', 'agent must reach the probe Service')
expect_http('outpost-031-040-02-02', 'drifter', METADATA, '200', 'outpost-031-040-02-02 must stay unchanged')
if wants('shuttle-blocked'):
    expect_http(NAMESPACE, 'shuttle', METADATA, 'denied', 'shuttle must not reach the metadata address')
