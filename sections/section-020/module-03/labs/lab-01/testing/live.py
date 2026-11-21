# Checks that read the running processes and files of this lab's node
# containers. check.py runs this file with NODE, WORKER, node_exec(),
# kubectl(), get() and wants() already defined.
import re
import time


def process_arguments(container, program):
    """Return the command line of the newest running process with this name."""
    found = node_exec(container, 'pgrep', '-n', '-f', '^(/[^ ]*/)?' + program + '( |$)', success=False).stdout.strip()
    assert found, program + ' is not running on ' + container
    raw = node_exec(container, 'cat', '/proc/' + found + '/cmdline', success=False).stdout
    arguments = [item for item in raw.split('\0') if item]
    assert arguments, program + ' stopped while it was read; try again'
    return arguments


def flag_value(arguments, name):
    """The value a single-value flag takes: the last occurrence wins."""
    value = None
    for position, item in enumerate(arguments):
        if item.startswith('--' + name + '='):
            value = item.split('=', 1)[1]
        elif item == '--' + name:
            following = arguments[position + 1] if position + 1 < len(arguments) else ''
            value = following if following and not following.startswith('-') else 'true'
    return value


def flag_list(arguments, name):
    """The items of a list flag: every occurrence adds its items."""
    items = []
    for position, item in enumerate(arguments):
        if item.startswith('--' + name + '='):
            listed = item.split('=', 1)[1]
        elif item == '--' + name and position + 1 < len(arguments):
            listed = arguments[position + 1]
        else:
            continue
        items += [part.strip() for part in listed.split(',') if part.strip()]
    return items


def file_mode(container, path):
    result = node_exec(container, 'stat', '-c', '%a %U:%G', path, success=False)
    assert result.returncode == 0, path + ' is missing on ' + container
    mode, owner = result.stdout.split()
    return int(mode, 8), owner


def assert_mode_at_most(container, path, limit, owner='root:root'):
    mode, actual_owner = file_mode(container, path)
    assert mode & ~limit == 0, '%s has mode %o; it must be %o or stricter' % (path, mode, limit)
    if owner:
        assert actual_owner == owner, path + ' must be owned by ' + owner


def configz(node):
    return json.loads(kubectl('get', '--raw', '/api/v1/nodes/' + node + '/proxy/configz'))['kubeletconfig']


def assert_api_ready():
    assert kubectl('--request-timeout=5s', 'get', '--raw=/readyz') == 'ok', 'The API server must stay ready'


def assert_node_ready(node):
    status = get('node', node, namespace=None)['status']
    assert any(item['type'] == 'Ready' and item['status'] == 'True' for item in status['conditions']), node + ' must stay Ready'


# Keep every backup outside /etc/kubernetes/manifests: the kubelet starts every file there.
manifests = sorted(node_exec(NODE, 'ls', '-A', '/etc/kubernetes/manifests').stdout.split())
assert manifests == ['etcd.yaml', 'kube-apiserver.yaml', 'kube-controller-manager.yaml', 'kube-scheduler.yaml'], \
    '/etc/kubernetes/manifests must hold only the four control plane manifests, not ' + ', '.join(manifests)
arguments = process_arguments(NODE, 'kube-apiserver')
if wants('audit-policy'):
    policy = flag_value(arguments, 'audit-policy-file')
    assert policy == '/etc/kubernetes/policy/audit-policy.yaml', 'Set --audit-policy-file=/etc/kubernetes/policy/audit-policy.yaml'
    staged = node_exec(NODE, 'cat', '/opt/training/audit-policy.yaml').stdout
    used = node_exec(NODE, 'cat', policy, success=False).stdout
    assert used.strip() == staged.strip(), 'The policy file differs from the staged policy'
if wants('audit-log-retention'):
    for name in ('audit-log-maxage', 'audit-log-maxbackup', 'audit-log-maxsize'):
        value = flag_value(arguments, name)
        assert value and value.isdigit() and int(value) > 0, 'Set --' + name + ' to a number above zero'
if wants('audit-events-written'):
    path = flag_value(arguments, 'audit-log-path')
    assert path == '/var/log/kubernetes/audit/audit.log', 'Set --audit-log-path=/var/log/kubernetes/audit/audit.log'
    marker = 'audit-check-' + str(int(time.time()))
    kubectl('-n', NAMESPACE, 'create', 'configmap', marker)
    kubectl('-n', NAMESPACE, 'delete', 'configmap', marker)
    seen = False
    for attempt in range(10):
        if node_exec(NODE, 'grep', '-c', marker, path, success=False).returncode == 0:
            seen = True
            break
        time.sleep(2)
    assert seen, 'No audit event for the test request was found in ' + path
