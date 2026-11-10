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


STARFLEET = NAMESPACE
OUTPOST = 'outpost-031-040-03-02'
DOCK = 'dock-031-040-03-02'
RUNTIME_SOCKET = {OUTPOST + '/runtime-peek', STARFLEET + '/cri-helper'}
HOST_NETWORK = {DOCK + '/net-tool'}
for pod in (OUTPOST + '/runtime-peek', STARFLEET + '/cri-helper', OUTPOST + '/log-reader', DOCK + '/net-tool'):
    namespace, name = pod.split('/')
    assert get('pod', name, namespace)['status'].get('phase') == 'Running', 'Pod %s must still be running' % pod


def listed():
    data = get('configmap', 'exposed-pods', DOCK).get('data', {})
    lines = [line.strip() for line in data.get('pods', '').splitlines() if line.strip()]
    extra = sorted(set(lines) - RUNTIME_SOCKET - HOST_NETWORK)
    assert not extra, 'ConfigMap exposed-pods lists pods that do not match: ' + ', '.join(extra)
    assert len(lines) == len(set(lines)), 'ConfigMap exposed-pods lists a pod twice'
    return set(lines)


if wants('runtime-socket-pods'):
    missing = sorted(RUNTIME_SOCKET - listed())
    assert not missing, 'ConfigMap exposed-pods must list the pods that mount the runtime socket: ' + ', '.join(missing)
if wants('host-network-pods'):
    missing = sorted(HOST_NETWORK - listed())
    assert not missing, 'ConfigMap exposed-pods must list the pods that use the host network: ' + ', '.join(missing)
