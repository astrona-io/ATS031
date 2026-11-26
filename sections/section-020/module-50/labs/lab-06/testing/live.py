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




def assert_write_access_removed():
    for verb in ('update', 'patch'):
        answer = command(['kubectl', 'auth', 'can-i', verb, 'configmap/coredns', '-n', 'kube-system', '--as=system:serviceaccount:outpost-031-020-05-06:default'], success=False).stdout.strip()
        assert answer == 'no', 'The default service account of outpost-031-020-05-06 can still ' + verb + ' the coredns ConfigMap'


if wants('coredns-write-access'):
    assert_write_access_removed()
if wants('coredns-rbac-kept'):
    assert_write_access_removed()
    coredns_role = kubectl('get', 'clusterrolebinding', 'system:coredns', '-o', 'jsonpath={.roleRef.name}')
    assert coredns_role == 'system:coredns', 'Keep the system:coredns ClusterRoleBinding'
    subjects = get('clusterrolebinding', 'system:coredns', namespace=None).get('subjects') or []
    assert any(item.get('kind') == 'ServiceAccount' and item.get('name') == 'coredns' and item.get('namespace') == 'kube-system' for item in subjects), \
        'Keep the coredns service account in the system:coredns ClusterRoleBinding'
    get('serviceaccount', 'coredns', namespace='kube-system')
    for resource in ('endpoints', 'services', 'pods', 'namespaces', 'endpointslices.discovery.k8s.io'):
        answer = command(['kubectl', 'auth', 'can-i', 'watch', resource, '--as=system:serviceaccount:kube-system:coredns'], success=False).stdout.strip()
        assert answer == 'yes', 'Do not change the system:coredns ClusterRole: coredns must still watch ' + resource
if wants('pod-records'):
    corefile = get('configmap', 'coredns', namespace='kube-system')['data']['Corefile']
    assert not re.search(r'^[^#]*\bpods\s+insecure\b', corefile, re.M), 'The Corefile still uses pods insecure'
    assert re.search(r'^\s*pods\s+(verified|disabled)\s*(#.*)?$', corefile, re.M), 'Set pods verified or pods disabled in the Corefile'
    lookup = command(['kubectl', '-n', NAMESPACE, 'exec', 'shuttle', '--', 'nslookup', 'probe.' + NAMESPACE + '.svc.cluster.local'], success=False)
    assert lookup.returncode == 0, 'The shuttle pod can no longer resolve the probe Service'
