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


staged = node_exec(NODE, 'cat', '/var/lib/astrona-lab/020-01-03-staged', success=False)
assert staged.returncode == 0, 'The record of the starting settings is missing; start the lab again'
chosen = dict(line.split('=', 1) for line in staged.stdout.split())
running = process_arguments(NODE, 'kube-apiserver')
assert (flag_value(running, 'profiling') or 'true') == chosen['profiling'], 'Do not change the --profiling setting of the API server'
assert flag_value(running, 'authorization-mode') == 'Node,RBAC', 'Do not change the --authorization-mode of the API server'
assert flag_value(process_arguments(NODE, 'etcd'), 'client-cert-auth') == 'true', 'Do not change the --client-cert-auth setting of etcd'
assert node_exec(NODE, 'stat', '-c', '%a', '/var/lib/etcd').stdout.strip() == chosen['data_mode'], 'Do not change the mode of /var/lib/etcd'
saved = get('configmap', 'manual-audit').get('data', {})
if wants('apiserver-values'):
    arguments = process_arguments(NODE, 'kube-apiserver')
    assert saved.get('apiserver-authorization-mode') == flag_value(arguments, 'authorization-mode'), 'apiserver-authorization-mode differs from the running API server'
    assert saved.get('apiserver-profiling') == (flag_value(arguments, 'profiling') or 'true'), 'apiserver-profiling differs from the running API server'
if wants('etcd-values'):
    arguments = process_arguments(NODE, 'etcd')
    assert saved.get('etcd-client-cert-auth') == (flag_value(arguments, 'client-cert-auth') or 'false'), 'etcd-client-cert-auth differs from the running etcd'
    mode = node_exec(NODE, 'stat', '-c', '%a', '/var/lib/etcd').stdout.strip()
    assert saved.get('etcd-data-dir-mode') == mode, 'etcd-data-dir-mode differs from the mode of /var/lib/etcd'
