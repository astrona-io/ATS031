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


OUTPOST = 'outpost-031-040-01-01'
STARFLEET_EGRESS = {
    'podSelector': {},
    'policyTypes': ['Egress'],
    'egress': [
        {'to': [{'namespaceSelector': {'matchLabels': {'kubernetes.io/metadata.name': 'kube-system'}}, 'podSelector': {'matchLabels': {'k8s-app': 'kube-dns'}}}],
         'ports': [{'protocol': 'UDP', 'port': 53}, {'protocol': 'TCP', 'port': 53}]},
        {'to': [{'podSelector': {'matchLabels': {'app': 'probe'}}}], 'ports': [{'protocol': 'TCP', 'port': 8080}]},
    ],
}


def relay_pods():
    pods = json.loads(kubectl('-n', NAMESPACE, 'get', 'pods', '-l', 'app=relay', '-o', 'json'))['items']
    return [pod for pod in pods if not pod['metadata'].get('deletionTimestamp')]


def running_relay():
    pods = [pod for pod in relay_pods() if pod['status'].get('phase') == 'Running']
    assert len(pods) == 1, 'Exactly one relay pod must be running, found %d' % len(pods)
    return pods[0]


try:
    relay = get('deployment', 'relay')
    status = relay.get('status', {})
    assert status.get('observedGeneration', 0) >= relay['metadata']['generation'], 'The relay Deployment has not finished its rollout'
    assert status.get('availableReplicas', 0) == relay['spec'].get('replicas', 1) == status.get('updatedReplicas', 0), 'The relay Deployment must be available with all replicas updated'
    simulator_pod = get('pod', 'metadata-simulator')
    simulator = 'http://%s:8080/' % simulator_pod['status']['podIP']
    expect_http(OUTPOST, 'drifter', simulator, '200', 'drifter must still reach metadata-simulator, so the listener works')
    policy = get('networkpolicy', 'starfleet-egress')
    assert policy['spec'] == STARFLEET_EGRESS, 'Do not change the NetworkPolicy starfleet-egress'
    if wants('pod-network'):
        assert not relay['spec']['template']['spec'].get('hostNetwork'), 'The relay pod template must not use hostNetwork'
        pod = running_relay()
        assert not pod['spec'].get('hostNetwork'), 'The running relay pod still uses the network of the node'
        assert pod['status'].get('podIP') != pod['status'].get('hostIP'), 'The running relay pod must have its own pod IP address'
    if wants('metadata-blocked'):
        name = running_relay()['metadata']['name']
        expect_http(NAMESPACE, name, simulator, 'denied', 'relay must not reach metadata-simulator')
        expect_http(NAMESPACE, name, 'http://probe/', '200', 'relay must still reach the probe Service by name')
finally:
    remove_test_pods()
