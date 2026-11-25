#!/usr/bin/env python3
"""Grader engine: reads requirements.json and runs bounded checks in one context."""
import json
from pathlib import Path
import subprocess
import sys

DIRECTORY = Path(__file__).resolve().parent


def run(args, timeout=20):
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None


def kubectl(*args):
    result = run(['kubectl', *args])
    assert result is not None and result.returncode == 0, 'Required kubectl command failed: ' + ' '.join(args[:4])
    return result.stdout.strip()


def get_json(*args):
    return json.loads(kubectl(*args, '-o', 'json'))


def node_addresses():
    nodes = get_json('get', 'nodes')['items']
    result = {}
    for node in nodes:
        address = next(a['address'] for a in node['status']['addresses'] if a['type'] == 'InternalIP')
        key = 'control_plane_ip' if 'node-role.kubernetes.io/control-plane' in node['metadata'].get('labels', {}) else 'worker_ip'
        result[key] = address
    return result


def http_status(source, url):
    namespace, pod = source.split('/')
    result = run(['kubectl', '-n', namespace, 'exec', pod, '--', 'curl', '-sk', '-m', '3', '-o', '/dev/null', '-w', '%{http_code}', url], timeout=25)
    if result is None:
        return 'denied'
    if result.returncode != 0 and result.stdout.strip() in ('', '000'):
        return 'denied'
    return result.stdout.strip()


def check_http(check, addresses):
    url = check['url'].format(**addresses)
    actual = http_status(check['from'], url)
    assert actual == check['expect'], '%s: request from %s to %s gave %s, expected %s' % (check['label'], check['from'], url, actual, check['expect'])


def check_labels(check, addresses):
    namespace, name = check['pod'].split('/')
    labels = get_json('-n', namespace, 'get', 'pod', name)['metadata'].get('labels', {})
    for key, value in check.get('has', {}).items():
        assert labels.get(key) == value, 'Pod %s must keep label %s=%s' % (check['pod'], key, value)
    for key in check.get('lacks', []):
        assert key not in labels, 'Pod %s must not have label %s' % (check['pod'], key)


def check_selects_all(check, addresses):
    policies = get_json('-n', check['namespace'], 'get', 'networkpolicy')['items']
    assert any(not p['spec'].get('podSelector') and 'Egress' in p['spec'].get('policyTypes', []) for p in policies), \
        'Namespace %s needs an egress policy that selects all pods' % check['namespace']


def check_configmap_lines(check, addresses):
    data = get_json('-n', check['namespace'], 'get', 'configmap', check['name'])['data']
    lines = sorted(line.strip() for line in data.get(check['key'], '').splitlines() if line.strip())
    assert lines == sorted(check['expected']), 'ConfigMap %s key %s must list exactly: %s' % (check['name'], check['key'], ', '.join(sorted(check['expected'])))


def check_pods_exist(check, addresses):
    for pod in check['pods']:
        namespace, name = pod.split('/')
        phase = get_json('-n', namespace, 'get', 'pod', name)['status'].get('phase')
        assert phase == 'Running', 'Pod %s must still be running' % pod


def check_no_socket_mount(check, addresses):
    deployment = get_json('-n', check['namespace'], 'get', 'deployment', check['name'])
    spec = deployment['spec']['template']['spec']
    for volume in spec.get('volumes', []):
        path = volume.get('hostPath', {}).get('path', '')
        assert 'containerd' not in path and 'docker.sock' not in path and 'crio' not in path, 'Deployment %s still mounts a runtime path' % check['name']
    for container in spec['containers']:
        for mount in container.get('volumeMounts', []):
            assert 'containerd' not in mount['mountPath'], 'Deployment %s still mounts a runtime path' % check['name']
    status = deployment['status']
    assert status.get('readyReplicas', 0) == deployment['spec'].get('replicas', 1) == status.get('updatedReplicas', 0), 'Deployment %s must be rolled out and ready' % check['name']


CHECKS = {
    'http': check_http,
    'labels': check_labels,
    'selects_all': check_selects_all,
    'configmap_lines': check_configmap_lines,
    'pods_exist': check_pods_exist,
    'no_socket_mount': check_no_socket_mount,
}


def main():
    requirements = json.loads((DIRECTORY / 'requirements.json').read_text())
    assert kubectl('config', 'current-context') == requirements['context'], 'Refusing to operate on another Kubernetes context'
    addresses = node_addresses()
    for check in requirements['checks']:
        CHECKS[check['type']](check, addresses)
    print('Required result verified')


if __name__ == '__main__':
    try:
        main()
    except (AssertionError, KeyError, ValueError, StopIteration, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
