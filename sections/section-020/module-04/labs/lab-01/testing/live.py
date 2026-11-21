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


def etcdctl(*arguments):
    """Run etcdctl inside the etcd pod with the health check client certificate."""
    result = subprocess.run(['kubectl', '-n', 'kube-system', 'exec', 'etcd-' + NODE, '--', 'etcdctl',
                             '--endpoints=https://127.0.0.1:2379', '--cacert=/etc/kubernetes/pki/etcd/ca.crt',
                             '--cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt',
                             '--key=/etc/kubernetes/pki/etcd/healthcheck-client.key'] + list(arguments),
                            capture_output=True, timeout=30)
    assert result.returncode == 0, 'Could not run etcdctl in the etcd pod'
    return result.stdout

import base64

# Keep every backup outside /etc/kubernetes/manifests: the kubelet starts every file there.
manifests = sorted(node_exec(NODE, 'ls', '-A', '/etc/kubernetes/manifests').stdout.split())
assert manifests == ['etcd.yaml', 'kube-apiserver.yaml', 'kube-controller-manager.yaml', 'kube-scheduler.yaml'], \
    '/etc/kubernetes/manifests must hold only the four control plane manifests, not ' + ', '.join(manifests)

if wants('encryption-provider'):
    path = flag_value(process_arguments(NODE, 'kube-apiserver'), 'encryption-provider-config')
    assert path == '/etc/kubernetes/enc/encryption-config.yaml', 'Set --encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml'
    text = node_exec(NODE, 'cat', path).stdout
    named = re.search(r'''^\s*-\s*["']?secrets["']?\s*(#.*)?$''', text, re.M) or \
        re.search(r'''^\s*resources\s*:\s*\[[^\]]*["']?\bsecrets\b["']?''', text, re.M)
    assert named, 'The configuration must name the resource secrets'
    providers = re.findall(r'''^\s*-\s*["']?(aescbc|aesgcm|secretbox|kms|identity)["']?\s*:''', text, re.M)
    assert providers[:1] == ['aescbc'], 'The first provider must be aescbc'
    assert 'identity' in providers[1:], 'identity must follow aescbc in the provider list'
    key = re.search(r'''^\s*secret\s*:\s*["']?([A-Za-z0-9+/=]+)["']?\s*(#.*)?$''', text, re.M)
    assert key, 'The aescbc provider needs a key with a secret'
    try:
        length = len(base64.b64decode(key.group(1), validate=True))
    except Exception:
        length = 0
    assert length == 32, 'The aescbc key must be 32 random bytes, base64 encoded'
    assert_mode_at_most(NODE, path, 0o600, owner=None)
if wants('secret-encrypted'):
    stored = etcdctl('get', '/registry/secrets/' + NAMESPACE + '/launch-code', '--print-value-only')
    assert b'k8s:enc:aescbc:v1:' in stored, 'The Secret is not stored with the aescbc provider'
    assert b'warp-nine-launch' not in stored, 'The Secret is still readable in etcd'
encoded = kubectl('-n', NAMESPACE, 'get', 'secret', 'launch-code', '-o', 'jsonpath={.data.code}')
assert base64.b64decode(encoded) == b'warp-nine-launch', 'The API no longer returns the Secret value'
