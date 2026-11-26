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


staged = node_exec(NODE, 'cat', '/var/lib/astrona-lab/020-04-02-staged', success=False)
assert staged.returncode == 0, 'The record of the starting settings is missing; start the lab again'
assert node_exec(NODE, 'sha256sum', '--check', '--quiet', '/var/lib/astrona-lab/020-04-02-staged', success=False).returncode == 0, \
    'Do not change the cluster: a control plane manifest or the kubelet configuration changed'
arguments = process_arguments(NODE, 'kube-apiserver')
saved = get('configmap', 'etcd-connection').get('data', {})


def assert_recorded(pairs):
    for key, flag in pairs:
        assert saved.get(key, '').strip(), 'The ConfigMap etcd-connection has no key ' + key
        expected = flag_value(arguments, flag)
        assert expected, 'kube-apiserver has no --' + flag + ' flag'
        assert saved.get(key, '').strip() == expected, 'The key ' + key + ' differs from --' + flag + ' of the running API server'


if wants('server-recorded'):
    assert_recorded([('servers', 'etcd-servers')])
if wants('credentials-recorded'):
    assert_recorded([('client-certificate', 'etcd-certfile'), ('client-key', 'etcd-keyfile')])
if wants('ca-recorded'):
    assert_recorded([('ca-file', 'etcd-cafile')])
