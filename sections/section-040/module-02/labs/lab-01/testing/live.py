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


OUTPOST = 'outpost-031-040-02-01'
METADATA = 'http://169.254.169.254/latest/meta-data/'
PROBE_STARFLEET = 'http://probe.' + NAMESPACE + '.svc.cluster.local/'
try:
    assert get('pod', 'drifter', OUTPOST)['status'].get('phase') == 'Running', 'Pod %s/drifter must still be running' % OUTPOST
    expect_http('metadata-stub-031-040-02-01', 'control', METADATA, '200', 'The control pod must still reach the metadata server')
    expect_http(NAMESPACE, 'shuttle', METADATA, '200', 'Namespace %s must stay unchanged' % NAMESPACE)
    expect_http(NAMESPACE, 'agent', METADATA, '200', 'Namespace %s must stay unchanged' % NAMESPACE)
    expect_http('dock-031-040-02-01', 'tender', METADATA, '200', 'Namespace dock-031-040-02-01 must stay unchanged')
    if wants('metadata-blocked'):
        expect_http(OUTPOST, 'drifter', METADATA, 'denied', 'drifter must not reach the metadata address')
        expect_http(OUTPOST, 'drifter', 'http://probe/', '200', 'drifter must still reach the probe Service in its namespace')
        expect_http(OUTPOST, 'drifter', PROBE_STARFLEET, '200', 'drifter must still reach a Service in another namespace by DNS name')
    if wants('whole-namespace'):
        new_pod = test_pod(OUTPOST)
        expect_http(OUTPOST, new_pod, METADATA, 'denied', 'A new pod in %s must not reach the metadata address' % OUTPOST)
        expect_http(OUTPOST, new_pod, 'http://probe/', '200', 'A new pod in %s must still reach the probe Service' % OUTPOST)
        expect_http(OUTPOST, new_pod, PROBE_STARFLEET, '200', 'A new pod in %s must still reach other Services by DNS name' % OUTPOST)
finally:
    remove_test_pods()
