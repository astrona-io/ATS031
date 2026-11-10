# Guard: the API server static pod of this cluster is running and ready.
resource_check({'kind': 'pod', 'name': 'kube-apiserver-' + NODE, 'namespace': 'kube-system', 'expected': {}, 'state': 'pod'})
_pod = get('pod', 'kube-apiserver-' + NODE, namespace='kube-system')
if wants('api-profiling-disabled'):
    assert '--profiling=false' in _pod['spec']['containers'][0]['command'], 'Disable the effective API profiling flag'
