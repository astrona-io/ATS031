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


def node_ip(node):
    return next(address['address'] for address in get('node', node, namespace=None)['status']['addresses'] if address['type'] == 'InternalIP')


OUTPOST = 'outpost-031-040-03-02'
PROBE_STARFLEET = 'http://probe.' + NAMESPACE + '.svc.cluster.local/'
worker_ip = node_ip(WORKER)
control_plane_ip = node_ip(NODE)
try:
    expect_http(NAMESPACE, 'shuttle', 'http://%s:10255/pods' % worker_ip, '200', NAMESPACE + ' must stay unchanged')
    expect_http('dock-031-040-03-02', 'tender', 'http://%s:10255/pods' % worker_ip, '200', 'dock-031-040-03-02 must stay unchanged')
    expect_http('metadata-stub-031-040-03-02', 'control', 'http://%s:10255/pods' % worker_ip, '200', 'The control pod must still reach the read-only port')
    expect_http(OUTPOST, 'drifter', 'http://probe/', '200', 'drifter must reach the probe Service')
    expect_http(OUTPOST, 'drifter', PROBE_STARFLEET, '200', 'drifter must reach a Service in another namespace by DNS name')
    if wants('kubelet-https-port'):
        expect_http(OUTPOST, 'drifter', 'https://%s:10250/pods' % worker_ip, 'denied', 'drifter must not reach the worker kubelet port')
        expect_http(OUTPOST, 'drifter', 'https://%s:10250/pods' % control_plane_ip, 'denied', 'drifter must not reach the control plane kubelet port')
    if wants('kubelet-read-only-port'):
        expect_http(OUTPOST, 'drifter', 'http://%s:10255/pods' % worker_ip, 'denied', 'drifter must not reach the worker read-only port')
    if wants('whole-namespace'):
        new_pod = test_pod(OUTPOST)
        expect_http(OUTPOST, new_pod, 'https://%s:10250/pods' % worker_ip, 'denied', 'A new pod in %s must not reach the worker kubelet port' % OUTPOST)
        expect_http(OUTPOST, new_pod, 'https://%s:10250/pods' % control_plane_ip, 'denied', 'A new pod in %s must not reach the control plane kubelet port' % OUTPOST)
        expect_http(OUTPOST, new_pod, 'http://%s:10255/pods' % worker_ip, 'denied', 'A new pod in %s must not reach the worker read-only port' % OUTPOST)
        expect_http(OUTPOST, new_pod, 'http://probe/', '200', 'A new pod in %s must still reach the probe Service' % OUTPOST)
        expect_http(OUTPOST, new_pod, PROBE_STARFLEET, '200', 'A new pod in %s must still reach other Services by DNS name' % OUTPOST)
finally:
    remove_test_pods()
