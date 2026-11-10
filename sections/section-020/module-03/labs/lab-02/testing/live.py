# Guard: the API server static pod of this cluster is running and ready.
resource_check({'kind': 'pod', 'name': 'kube-apiserver-' + NODE, 'namespace': 'kube-system', 'expected': {}, 'state': 'pod'})
_node = NODE
_label = subprocess.run([ENGINE, 'inspect', _node, '--format', '{{index .Config.Labels "io.x-k8s.kind.cluster"}}'], capture_output=True, text=True, timeout=20).stdout.strip()
assert _label == CLUSTER, 'Refusing an unrelated node container'
_pod = get('pod', 'kube-apiserver-' + _node, namespace='kube-system')
if wants('api-profiling-disabled'):
    assert '--profiling=false' in _pod['spec']['containers'][0]['command'], 'The API server must run with --profiling=false'
if wants('api-manifest-permissions'):
    _stat = subprocess.run([ENGINE, 'exec', _node, 'stat', '-c', '%a %U:%G', '/etc/kubernetes/manifests/kube-apiserver.yaml'], capture_output=True, text=True, timeout=20)
    assert _stat.returncode == 0 and _stat.stdout.strip() == '600 root:root', 'The API server manifest must have mode 600 and owner root:root'
