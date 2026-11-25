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
CLIENTS = {
    'starfleet': ('starfleet-031-040-02-03', 'shuttle'),
    'outpost': ('outpost-031-040-02-03', 'drifter'),
    'dock': ('dock-031-040-02-03', 'tender'),
}


def check_repaired(role):
    namespace, client = CLIENTS[role]
    assert get('pod', client, namespace)['status'].get('phase') == 'Running', 'Pod %s/%s must still be running' % (namespace, client)
    pods = [client, test_pod(namespace)]
    if role == 'starfleet':
        assert get('pod', 'agent', namespace)['status'].get('phase') == 'Running', 'Pod %s/agent must still be running' % namespace
        pods += ['agent', test_pod(namespace, 'role=cloud-agent')]
    for pod in pods:
        expect_http(namespace, pod, METADATA, 'denied', 'Pod %s/%s must not reach the metadata address' % (namespace, pod))
        expect_http(namespace, pod, 'http://probe/', '200', 'Pod %s/%s must still reach the probe Service' % (namespace, pod))


try:
    expect_http('metadata-stub-031-040-02-03', 'control', METADATA, '200', 'The control pod must still reach the metadata server')
    for role in ('starfleet', 'outpost', 'dock'):
        if wants(role + '-repaired'):
            check_repaired(role)
finally:
    remove_test_pods()
