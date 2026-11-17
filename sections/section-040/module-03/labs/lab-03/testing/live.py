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


RUNTIME_PATHS = ('containerd', 'docker.sock', 'crio')


def runtime_host_paths(pod_spec):
    paths = [volume['hostPath']['path'] for volume in pod_spec.get('volumes', []) if 'hostPath' in volume]
    return [path for path in paths if any(word in path for word in RUNTIME_PATHS)]


def scanner_container(pod_spec):
    return next(container for container in pod_spec['containers'] if container['name'] == 'scanner')


def running_scanner_pod():
    pods = json.loads(kubectl('-n', NAMESPACE, 'get', 'pods', '-l', 'app=image-scanner', '-o', 'json'))['items']
    live = [pod for pod in pods if pod['status'].get('phase') == 'Running' and not pod['metadata'].get('deletionTimestamp')]
    assert len(live) == 1, 'Exactly one running image-scanner pod is expected, found %d; wait for the rollout to finish' % len(live)
    return live[0]


def in_pod(pod, *args):
    return run(['kubectl', '-n', NAMESPACE, 'exec', pod, '-c', 'scanner', '--', *args], 20)


rollout = run(['kubectl', '-n', NAMESPACE, 'rollout', 'status', 'deployment/image-scanner', '--timeout=60s'], 70)
assert rollout is not None and rollout.returncode == 0, 'The image-scanner Deployment must finish its rollout and be available'
template = get('deployment', 'image-scanner')['spec']['template']['spec']
volumes = {volume['name']: volume for volume in template.get('volumes', [])}
assert 'emptyDir' in volumes.get('scratch', {}), 'The scratch emptyDir volume must stay'
assert volumes.get('settings', {}).get('configMap', {}).get('name') == 'scanner-settings', 'The settings ConfigMap volume must stay'
mounts = {mount['name']: mount['mountPath'] for mount in scanner_container(template).get('volumeMounts', [])}
assert mounts.get('scratch') == '/scratch' and mounts.get('settings') == '/etc/scanner', 'The scanner container must keep its /scratch and /etc/scanner mounts'
shipper = get('deployment', 'log-shipper')['spec']['template']['spec']
assert [volume.get('hostPath', {}).get('path') for volume in shipper.get('volumes', [])] == ['/var/log'], 'The log-shipper Deployment must stay unchanged'
pod = running_scanner_pod()
pod_name = pod['metadata']['name']
settings = in_pod(pod_name, 'cat', '/etc/scanner/targets')
assert settings is not None and settings.returncode == 0 and 'registry.dock.internal' in settings.stdout, 'The scanner must still read its settings from /etc/scanner'

if wants('socket-removed'):
    assert not runtime_host_paths(template), 'The Deployment template still mounts a container runtime path: %s' % runtime_host_paths(template)
    assert not runtime_host_paths(pod['spec']), 'The running pod still mounts a container runtime path; wait for the new pod'
    probe_socket = in_pod(pod_name, 'sh', '-c', 'test -e /host/run/containerd/containerd.sock || test -e /run/containerd/containerd.sock')
    assert probe_socket is not None and probe_socket.returncode != 0, 'The containerd socket is still visible inside the running scanner pod'

if wants('runs-as-non-root'):
    container_context = scanner_container(template).get('securityContext', {})
    pod_context = template.get('securityContext', {})
    non_root = container_context.get('runAsNonRoot', pod_context.get('runAsNonRoot'))
    assert non_root is True, 'The scanner container must set runAsNonRoot: true, in the pod or the container securityContext'
    user = in_pod(pod_name, 'id', '-u')
    assert user is not None and user.returncode == 0, 'Could not read the user id in the scanner pod'
    assert user.stdout.strip() != '0', 'The scanner process still runs as user id 0'
