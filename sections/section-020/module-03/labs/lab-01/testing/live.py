import time
_node = 'astro-ats-031-lab-020-03-01-control-plane'
_label = subprocess.run(['podman', 'inspect', _node, '--format', '{{index .Config.Labels "io.x-k8s.kind.cluster"}}'], capture_output=True, text=True, timeout=20).stdout.strip()
assert _label == 'astro-ats-031-lab-020-03-01', 'Refusing an unrelated node container'
_pod = get('pod', 'kube-apiserver-' + _node, namespace='kube-system')
_args = _pod['spec']['containers'][0]['command']
def _flag(name):
    return [item.split('=', 1)[1] for item in _args if item.startswith('--' + name + '=')]
for _name in ('audit-policy-file', 'audit-log-path', 'audit-log-maxage', 'audit-log-maxbackup', 'audit-log-maxsize'):
    assert _flag(_name), 'API server flag is missing: --' + _name
_log_path = _flag('audit-log-path')[0]
_marker = 'audit-check-' + str(int(time.time()))
command(['kubectl', '-n', 'starfleet', 'create', 'configmap', _marker])
command(['kubectl', '-n', 'starfleet', 'get', 'configmap', _marker])
command(['kubectl', '-n', 'starfleet', 'delete', 'configmap', _marker])
_seen = False
for _attempt in range(10):
    _found = subprocess.run(['podman', 'exec', _node, 'grep', '-c', _marker, _log_path], capture_output=True, text=True, timeout=20)
    if _found.returncode == 0:
        _seen = True
        break
    time.sleep(2)
assert _seen, 'No audit event for the test request was found in the audit log'
