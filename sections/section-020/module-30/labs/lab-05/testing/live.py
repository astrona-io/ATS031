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


if wants('noderestriction-enabled'):
    arguments = process_arguments(NODE, 'kube-apiserver')
    assert 'NodeRestriction' in flag_list(arguments, 'enable-admission-plugins'), 'Add NodeRestriction to --enable-admission-plugins'
    assert 'NodeRestriction' not in flag_list(arguments, 'disable-admission-plugins'), 'NodeRestriction must not be disabled'
if wants('admission-plugins-kept'):
    # The plugin is added to the list, not swapped in: LimitRanger stays next to it.
    enabled = flag_list(process_arguments(NODE, 'kube-apiserver'), 'enable-admission-plugins')
    assert 'NodeRestriction' in enabled and 'LimitRanger' in enabled, 'Add NodeRestriction to --enable-admission-plugins and keep LimitRanger'
if wants('node-label-denied'):
    attempt = node_exec(WORKER, 'kubectl', '--kubeconfig', '/etc/kubernetes/kubelet.conf', 'label', 'node', WORKER, 'node-restriction.kubernetes.io/lab-check=kubelet', '--overwrite', success=False)
    if attempt.returncode == 0:
        kubectl('label', 'node', WORKER, 'node-restriction.kubernetes.io/lab-check-')
    assert attempt.returncode != 0, 'The kubelet of the node can still set a node-restriction.kubernetes.io/ label'
    assert 'forbidden' in (attempt.stdout + attempt.stderr).lower(), 'The label request failed for another reason than an admission denial'
