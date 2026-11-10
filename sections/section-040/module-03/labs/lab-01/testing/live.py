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


def node_ip(node):
    return next(a['address'] for a in get('node', node, namespace=None)['status']['addresses'] if a['type'] == 'InternalIP')


def selects_all_egress(namespace):
    policies = json.loads(kubectl('-n', namespace, 'get', 'networkpolicy', '-o', 'json'))['items']
    return any(not p['spec'].get('podSelector') and 'Egress' in p['spec'].get('policyTypes', []) for p in policies)


OUTPOST = 'outpost-031-040-03-01'
worker_ip = node_ip(WORKER)
control_plane_ip = node_ip(NODE)
expect_http(OUTPOST, 'drifter', 'http://probe/', '200', 'drifter must reach the probe Service')
expect_http(OUTPOST, 'drifter', 'http://probe.' + NAMESPACE + '.svc.cluster.local/', '200', 'DNS and cross-namespace Services must work')
expect_http(NAMESPACE, 'shuttle', 'http://%s:10255/pods' % worker_ip, '200', NAMESPACE + ' must stay unchanged')
expect_http('metadata-stub-031-040-03-01', 'control', 'http://%s:10255/pods' % worker_ip, '200', 'control pod must still reach the read-only port')
if wants('kubelet-https-port'):
    expect_http(OUTPOST, 'drifter', 'https://%s:10250/pods' % worker_ip, 'denied', 'drifter must not reach the worker kubelet port')
    expect_http(OUTPOST, 'drifter', 'https://%s:10250/pods' % control_plane_ip, 'denied', 'drifter must not reach the control plane kubelet port')
if wants('kubelet-read-only-port'):
    expect_http(OUTPOST, 'drifter', 'http://%s:10255/pods' % worker_ip, 'denied', 'drifter must not reach the worker read-only port')
if wants('whole-namespace'):
    assert selects_all_egress(OUTPOST), 'Namespace %s needs an egress policy that selects all pods' % OUTPOST
