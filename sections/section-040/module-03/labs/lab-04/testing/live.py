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


OUTPOST = 'outpost-031-040-03-04'
ORIGINAL_PODS = {NAMESPACE: ['net-tool', 'port-watch', 'tender'], OUTPOST: ['sniffer', 'debug-shell', 'drifter']}


def pods_in(namespace):
    return json.loads(kubectl('-n', namespace, 'get', 'pods', '-o', 'json'))['items']


def dry_run_pod(name, host_network):
    pod = {
        'apiVersion': 'v1', 'kind': 'Pod',
        'metadata': {'name': name, 'namespace': NAMESPACE},
        'spec': {'containers': [{'name': 'client', 'image': CLIENT_IMAGE, 'command': ['sleep', '60']}]},
    }
    if host_network:
        pod['spec']['hostNetwork'] = True
    result = run(['kubectl', 'create', '--dry-run=server', '-f', '-'], 30, stdin=json.dumps(pod))
    assert result is not None, 'The API server did not answer the dry run'
    return result


for namespace, names in ORIGINAL_PODS.items():
    running = {pod['metadata']['name'] for pod in pods_in(namespace) if pod['status'].get('phase') == 'Running'}
    missing = sorted(set(names) - running)
    assert not missing, 'Do not delete or recreate pods; not running in %s: %s' % (namespace, missing)

if wants('host-network-listed'):
    expected = {'%s/%s' % (namespace, pod['metadata']['name']) for namespace in ORIGINAL_PODS for pod in pods_in(namespace) if pod['spec'].get('hostNetwork')}
    result = run(['kubectl', '-n', NAMESPACE, 'get', 'configmap', 'host-network-pods', '-o', 'json'])
    assert result is not None and result.returncode == 0, 'The ConfigMap host-network-pods is missing in %s' % NAMESPACE
    value = json.loads(result.stdout).get('data', {}).get('pods', '')
    listed = [line.strip() for line in value.splitlines() if line.strip()]
    assert len(listed) == len(set(listed)), 'The list has duplicate lines'
    extra = sorted(set(listed) - expected)
    missing = sorted(expected - set(listed))
    assert not extra, 'These lines are not pods that use the host network: %s' % extra
    assert not missing, 'The list misses %d pod(s) that use the host network' % len(missing)

if wants('admission-blocks-host-network'):
    labels = get('namespace', NAMESPACE, namespace=None)['metadata'].get('labels', {})
    level = labels.get('pod-security.kubernetes.io/enforce')
    assert level == 'baseline', 'The namespace %s must enforce the baseline Pod Security level, found %s' % (NAMESPACE, level)
    blocked = dry_run_pod('grader-host-network', True)
    assert blocked.returncode != 0 and 'hostNetwork' in (blocked.stderr + blocked.stdout), 'A new pod with hostNetwork: true must be rejected in %s' % NAMESPACE
    plain = dry_run_pod('grader-plain', False)
    assert plain.returncode == 0, 'An ordinary new pod must still be accepted in %s: %s' % (NAMESPACE, plain.stderr.strip()[:200])
