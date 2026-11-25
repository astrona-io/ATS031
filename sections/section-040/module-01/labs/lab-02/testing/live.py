import time
import uuid

CLIENT_IMAGE = 'docker.io/curlimages/curl:8.11.1'
TEST_PODS = []


def run(args, timeout=30, stdin=None):
    """Run a command and return the result, or None when it does not finish in time."""
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=timeout, input=stdin)
    except subprocess.TimeoutExpired:
        return None


def http_status(namespace, pod, url):
    """HTTP status code of a request from a pod, or 'denied' when no HTTP answer arrives."""
    result = run(['kubectl', '-n', namespace, 'exec', pod, '--', 'curl', '-sk', '-m', '3', '-o', '/dev/null', '-w', '%{http_code}', url], 25)
    if result is None:
        return 'denied'
    output = result.stdout.strip()
    if result.returncode != 0 and output in ('', '000'):
        return 'denied'
    return output


def expect_http(namespace, pod, url, expected, label, attempts=3):
    """Retry a few times: the network plugin needs a moment for a new pod or policy."""
    actual = None
    for attempt in range(attempts):
        actual = http_status(namespace, pod, url)
        if actual == expected:
            return
        time.sleep(2)
    raise AssertionError('%s: request from %s/%s to %s gave %s, expected %s' % (label, namespace, pod, url, actual, expected))


def test_pod(namespace, labels=None):
    """Start a new client pod in a namespace, as a new workload would start, and wait until it is ready."""
    name = 'grader-' + uuid.uuid4().hex[:6]
    args = ['kubectl', '-n', namespace, 'run', name, '--image=' + CLIENT_IMAGE, '--restart=Never']
    if labels:
        args.append('--labels=' + labels)
    result = run(args + ['--command', '--', 'sleep', '600'])
    assert result is not None and result.returncode == 0, 'Could not start a test pod in namespace %s' % namespace
    TEST_PODS.append((namespace, name))
    ready = run(['kubectl', '-n', namespace, 'wait', '--for=condition=Ready', 'pod/' + name, '--timeout=90s'], 100)
    assert ready is not None and ready.returncode == 0, 'The test pod %s/%s did not become ready' % (namespace, name)
    return name


def remove_test_pods():
    for namespace, name in TEST_PODS:
        run(['kubectl', '-n', namespace, 'delete', 'pod', name, '--grace-period=0', '--force', '--wait=false'], 30)
    del TEST_PODS[:]


OUTPOST = 'outpost-031-040-01-02'


def pod_url(name, namespace):
    pod = get('pod', name, namespace)
    assert pod['status'].get('podIP'), 'Pod %s/%s has no IP address' % (namespace, name)
    return 'http://%s:8080/' % pod['status']['podIP']


try:
    courier = get('pod', 'courier')
    assert courier['metadata'].get('labels', {}).get('app') == 'courier', 'Pod %s/courier must keep label app=courier' % NAMESPACE
    assert courier['status'].get('phase') == 'Running', 'Pod %s/courier must be running' % NAMESPACE
    simulator = pod_url('metadata-simulator', NAMESPACE)
    beacon = pod_url('beacon', OUTPOST)
    expect_http(OUTPOST, 'drifter', simulator, '200', 'drifter must still reach metadata-simulator, so the listener works')
    expect_http(OUTPOST, 'drifter', beacon, '200', 'drifter must still reach beacon, so the listener works')
    if wants('metadata-blocked'):
        expect_http(NAMESPACE, 'courier', simulator, 'denied', 'courier must not reach metadata-simulator')
    if wants('dependencies-kept'):
        expect_http(NAMESPACE, 'courier', 'http://probe/', '200', 'courier must still reach the probe Service by name')
        expect_http(NAMESPACE, 'courier', beacon, 'denied', 'courier must not reach beacon, a destination that is not on the allow-list')
        new_pod = test_pod(NAMESPACE, 'app=courier')
        expect_http(NAMESPACE, new_pod, 'http://probe/', '200', 'A new pod with app=courier must reach the probe Service')
        expect_http(NAMESPACE, new_pod, simulator, 'denied', 'A new pod with app=courier must not reach metadata-simulator')
        other_pod = test_pod(NAMESPACE, 'app=other')
        expect_http(NAMESPACE, other_pod, beacon, '200', 'The NetworkPolicy must apply only to pods with app=courier: a pod with another label must still reach beacon')
finally:
    remove_test_pods()
