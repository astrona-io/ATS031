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


def selects_all_egress(namespace):
    policies = json.loads(kubectl('-n', namespace, 'get', 'networkpolicy', '-o', 'json'))['items']
    return any(not p['spec'].get('podSelector') and 'Egress' in p['spec'].get('policyTypes', []) for p in policies)


OUTPOST = 'outpost-031-040-02-01'
METADATA = 'http://169.254.169.254/latest/meta-data/'
assert get('pod', 'drifter', OUTPOST)['status'].get('phase') == 'Running', 'Pod %s/drifter must still be running' % OUTPOST
expect_http(OUTPOST, 'drifter', 'http://probe/', '200', 'drifter must reach the probe Service in its namespace')
expect_http(OUTPOST, 'drifter', 'http://probe.' + NAMESPACE + '.svc.cluster.local/', '200', 'drifter must reach a Service in another namespace by DNS name')
expect_http('metadata-stub-031-040-02-01', 'control', METADATA, '200', 'control pod must still reach the metadata server')
expect_http(NAMESPACE, 'shuttle', METADATA, '200', NAMESPACE + ' must stay unchanged')
if wants('metadata-blocked'):
    expect_http(OUTPOST, 'drifter', METADATA, 'denied', 'drifter must not reach the metadata address')
if wants('whole-namespace'):
    assert selects_all_egress(OUTPOST), 'Namespace %s needs an egress policy that selects all pods' % OUTPOST
