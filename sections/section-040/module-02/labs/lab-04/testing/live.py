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


METADATA = 'http://169.254.169.254/latest/meta-data/'
STARFLEET = 'starfleet-031-040-02-04'
OUTPOST = 'outpost-031-040-02-04'
DOCK = 'dock-031-040-02-04'


def check_covered(namespace, client):
    assert get('pod', client, namespace)['status'].get('phase') == 'Running', 'Pod %s/%s must still be running' % (namespace, client)
    for pod in (client, test_pod(namespace)):
        expect_http(namespace, pod, METADATA, 'denied', 'Pod %s/%s must not reach the metadata address' % (namespace, pod))
        expect_http(namespace, pod, 'http://probe/', '200', 'Pod %s/%s must still reach the probe Service' % (namespace, pod))


try:
    expect_http('metadata-stub-031-040-02-04', 'control', METADATA, '200', 'The control pod must still reach the metadata server')
    assert get('pod', 'agent', STARFLEET)['metadata'].get('labels', {}).get('role') == 'cloud-agent', 'Pod %s/agent must keep label role=cloud-agent' % STARFLEET
    assert 'role' not in get('pod', 'shuttle', STARFLEET)['metadata'].get('labels', {}), 'Pod %s/shuttle must not have label role' % STARFLEET
    expect_http(STARFLEET, 'shuttle', METADATA, 'denied', 'shuttle must stay blocked from the metadata address')
    if wants('outpost-covered'):
        check_covered(OUTPOST, 'drifter')
    if wants('dock-covered'):
        check_covered(DOCK, 'tender')
    if wants('agent-exception'):
        expect_http(STARFLEET, 'agent', METADATA, '200', 'agent must reach the metadata address')
        expect_http(STARFLEET, 'agent', 'http://probe/', '200', 'agent must still reach the probe Service')
        plain_pod = test_pod(STARFLEET)
        expect_http(STARFLEET, plain_pod, METADATA, 'denied', 'A new pod without the label must not reach the metadata address')
        expect_http(STARFLEET, plain_pod, 'http://probe/', '200', 'A new pod without the label must still reach the probe Service')
finally:
    remove_test_pods()
