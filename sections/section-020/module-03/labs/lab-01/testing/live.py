import time
# Guard: the API server static pod of this cluster is running and ready.
resource_check({'kind': 'pod', 'name': 'kube-apiserver-' + NODE, 'namespace': 'kube-system', 'expected': {}, 'state': 'pod'})
_node = NODE
_label = subprocess.run([ENGINE, 'inspect', _node, '--format', '{{index .Config.Labels "io.x-k8s.kind.cluster"}}'], capture_output=True, text=True, timeout=20).stdout.strip()
assert _label == CLUSTER, 'Refusing an unrelated node container'
_pod = get('pod', 'kube-apiserver-' + _node, namespace='kube-system')
_args = _pod['spec']['containers'][0]['command']
def _flag(name):
    return [item.split('=', 1)[1] for item in _args if item.startswith('--' + name + '=')]
if wants('audit-policy'):
    assert _flag('audit-policy-file'), 'API server flag is missing: --audit-policy-file'
if wants('audit-log-retention'):
    for _name in ('audit-log-maxage', 'audit-log-maxbackup', 'audit-log-maxsize'):
        assert _flag(_name), 'API server flag is missing: --' + _name
if wants('audit-events-written'):
    for _name in ('audit-policy-file', 'audit-log-path'):
        assert _flag(_name), 'API server flag is missing: --' + _name
    _log_path = _flag('audit-log-path')[0]
    _marker = 'audit-check-' + str(int(time.time()))
    command(['kubectl', '-n', 'starfleet-031-020-03-01', 'create', 'configmap', _marker])
    command(['kubectl', '-n', 'starfleet-031-020-03-01', 'get', 'configmap', _marker])
    command(['kubectl', '-n', 'starfleet-031-020-03-01', 'delete', 'configmap', _marker])
    _seen = False
    for _attempt in range(10):
        _found = subprocess.run([ENGINE, 'exec', _node, 'grep', '-c', _marker, _log_path], capture_output=True, text=True, timeout=20)
        if _found.returncode == 0:
            _seen = True
            break
        time.sleep(2)
    assert _seen, 'No audit event for the test request was found in the audit log'
