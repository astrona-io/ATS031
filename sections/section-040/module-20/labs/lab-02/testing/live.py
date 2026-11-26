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


def selector_matches(selector, labels):
    """Apply a Kubernetes label selector (matchLabels and matchExpressions)."""
    selector = selector or {}
    for key, value in (selector.get('matchLabels') or {}).items():
        if labels.get(key) != value:
            return False
    for expression in selector.get('matchExpressions') or []:
        key, operator, values = expression['key'], expression['operator'], expression.get('values') or []
        if operator == 'In' and labels.get(key) not in values:
            return False
        if operator == 'NotIn' and key in labels and labels[key] in values:
            return False
        if operator == 'Exists' and key not in labels:
            return False
        if operator == 'DoesNotExist' and key in labels:
            return False
    return True


def egress_policies(namespace, labels=None):
    """Names of the NetworkPolicies in a namespace that control egress, optionally only those that select the given pod labels."""
    policies = json.loads(kubectl('-n', namespace, 'get', 'networkpolicy', '-o', 'json'))['items']
    names = []
    for policy in policies:
        spec = policy.get('spec', {})
        if 'Egress' not in (spec.get('policyTypes') or []) and 'egress' not in spec:
            continue
        if labels is not None and not selector_matches(spec.get('podSelector'), labels):
            continue
        names.append(policy['metadata']['name'])
    return names


METADATA = 'http://169.254.169.254/latest/meta-data/'
AGENT_LABELS = {'app': 'agent', 'role': 'cloud-agent'}
SHUTTLE_LABELS = {'app': 'shuttle'}
try:
    assert get('pod', 'agent')['metadata'].get('labels', {}) == AGENT_LABELS, 'Do not add or remove labels on pod %s/agent' % NAMESPACE
    assert get('pod', 'shuttle')['metadata'].get('labels', {}) == SHUTTLE_LABELS, 'Do not add or remove labels on pod %s/shuttle' % NAMESPACE
    expect_http('metadata-stub-031-040-02-02', 'control', METADATA, '200', 'The control pod must still reach the metadata server')
    expect_http('outpost-031-040-02-02', 'drifter', METADATA, '200', 'outpost-031-040-02-02 must stay unchanged')
    expect_http('dock-031-040-02-02', 'tender', METADATA, '200', 'dock-031-040-02-02 must stay unchanged')
    if wants('shuttle-blocked'):
        assert egress_policies(NAMESPACE, SHUTTLE_LABELS), 'No egress NetworkPolicy in %s selects pod shuttle' % NAMESPACE
        expect_http(NAMESPACE, 'shuttle', METADATA, 'denied', 'shuttle must not reach the metadata address')
        expect_http(NAMESPACE, 'shuttle', 'http://probe/', '200', 'shuttle must reach the probe Service')
    if wants('agent-allowed'):
        assert egress_policies(NAMESPACE, AGENT_LABELS), 'No egress NetworkPolicy in %s selects pod agent' % NAMESPACE
        expect_http(NAMESPACE, 'agent', METADATA, '200', 'agent must reach the metadata address')
        expect_http(NAMESPACE, 'agent', 'http://probe/', '200', 'agent must reach the probe Service')
    if wants('label-decides'):
        assert egress_policies(NAMESPACE), 'No egress NetworkPolicy exists in %s' % NAMESPACE
        plain_pod = test_pod(NAMESPACE)
        labelled_pod = test_pod(NAMESPACE, 'role=cloud-agent')
        expect_http(NAMESPACE, plain_pod, METADATA, 'denied', 'A new pod without the label must not reach the metadata address')
        expect_http(NAMESPACE, plain_pod, 'http://probe/', '200', 'A new pod without the label must still reach the probe Service')
        expect_http(NAMESPACE, labelled_pod, METADATA, '200', 'A new pod with role=cloud-agent must reach the metadata address')
        expect_http(NAMESPACE, labelled_pod, 'http://probe/', '200', 'A new pod with role=cloud-agent must still reach the probe Service')
finally:
    remove_test_pods()
