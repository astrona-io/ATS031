PROTECTED_LABEL = 'node-restriction.kubernetes.io/dedicated'


def flag_values(arguments, flag):
    """The comma-separated values of one flag, or an empty list when it is missing."""
    prefix = flag + '='
    return [value for argument in arguments if argument.startswith(prefix) for value in argument[len(prefix):].split(',')]


def apiserver_arguments():
    """Command line of the kube-apiserver static pod on the control plane node."""
    pod = get('pod', 'kube-apiserver-' + NODE, namespace='kube-system')
    container = pod['spec']['containers'][0]
    return container.get('command', []) + container.get('args', [])


def worker_write(*args):
    """A server-side dry run of a write with the worker kubelet's own credential."""
    result = node_exec(WORKER, 'kubectl', '--kubeconfig', '/etc/kubernetes/kubelet.conf', '--request-timeout=10s', *args, '--dry-run=server', success=False)
    return result.returncode, (result.stdout + result.stderr).lower()


def expect_forbidden(label, *args):
    code, output = worker_write(*args)
    assert code != 0 and 'forbidden' in output, label + ': the worker credential was not refused by the API server'


if wants('admission-plugin'):
    arguments = apiserver_arguments()
    assert 'NodeRestriction' in flag_values(arguments, '--enable-admission-plugins'), 'The running kube-apiserver has no NodeRestriction in --enable-admission-plugins'
    assert 'NodeRestriction' not in flag_values(arguments, '--disable-admission-plugins'), 'The running kube-apiserver disables NodeRestriction'
    modes = flag_values(arguments, '--authorization-mode')
    assert 'Node' in modes and 'RBAC' in modes and 'AlwaysAllow' not in modes, 'The running kube-apiserver must use Node and RBAC authorization and not AlwaysAllow'

if wants('node-writes-refused'):
    expect_forbidden('Give the worker node the control plane role label', 'label', 'node', WORKER, 'node-role.kubernetes.io/control-plane=', '--overwrite')
    expect_forbidden('Set a protected label on the worker node', 'label', 'node', WORKER, 'node-restriction.kubernetes.io/lab-check=open', '--overwrite')

if wants('protected-label-removed'):
    worker = get('node', WORKER, namespace=None)
    assert PROTECTED_LABEL not in worker['metadata'].get('labels', {}), 'The worker node still carries ' + PROTECTED_LABEL
    assert any(condition['type'] == 'Ready' and condition['status'] == 'True' for condition in worker['status']['conditions']), 'The worker node must be Ready'
