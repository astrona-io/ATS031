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


def node_ready(node):
    conditions = get('node', node, namespace=None)['status'].get('conditions', [])
    return any(condition['type'] == 'Ready' and condition['status'] == 'True' for condition in conditions)


def running_read_only_port():
    """The value the running kubelet uses, from its configz endpoint through the API server."""
    result = run(['kubectl', 'get', '--raw', '/api/v1/nodes/%s/proxy/configz' % WORKER], 20)
    assert result is not None and result.returncode == 0, 'Could not read the running configuration of the worker kubelet'
    return json.loads(result.stdout)['kubeletconfig'].get('readOnlyPort', 0)


worker_ip = node_ip(WORKER)
try:
    assert node_ready(WORKER), 'The worker node must be Ready'
    expect_http(NAMESPACE, 'inspector', 'https://%s:10250/pods' % worker_ip, '401', 'The kubelet must still serve its HTTPS port 10250 and refuse anonymous requests', attempts=5)
    if wants('config-closed'):
        result = node_exec(WORKER, 'cat', '/var/lib/kubelet/config.yaml')
        values = [line.split(':', 1)[1].split('#', 1)[0].strip().strip('"\'') for line in result.stdout.splitlines() if line.startswith('readOnlyPort:')]
        assert all(value == '0' for value in values), 'readOnlyPort in /var/lib/kubelet/config.yaml on the worker must be 0 or absent, found %s' % values
    if wants('port-closed'):
        assert running_read_only_port() == 0, 'The running kubelet on the worker still uses a read-only port; restart it after changing the file'
        expect_http(NAMESPACE, 'inspector', 'http://%s:10255/pods' % worker_ip, 'denied', 'Port 10255 on the worker must not answer')
finally:
    remove_test_pods()
