_node = 'astro-ats-031-lab-020-03-02-control-plane'
_label = subprocess.run(['podman', 'inspect', _node, '--format', '{{index .Config.Labels "io.x-k8s.kind.cluster"}}'], capture_output=True, text=True, timeout=20).stdout.strip()
assert _label == 'astro-ats-031-lab-020-03-02', 'Refusing an unrelated node container'
_pod = get('pod', 'kube-apiserver-' + _node, namespace='kube-system')
assert '--profiling=false' in _pod['spec']['containers'][0]['command'], 'The API server must run with --profiling=false'
_stat = subprocess.run(['podman', 'exec', _node, 'stat', '-c', '%a %U:%G', '/etc/kubernetes/manifests/kube-apiserver.yaml'], capture_output=True, text=True, timeout=20)
assert _stat.returncode == 0 and _stat.stdout.strip() == '600 root:root', 'The API server manifest must have mode 600 and owner root:root'
