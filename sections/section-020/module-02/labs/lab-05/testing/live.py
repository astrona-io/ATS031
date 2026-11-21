# Checks that read the running processes and files of this lab's node
# containers. check.py runs this file with NODE, WORKER, node_exec(),
# kubectl(), get() and wants() already defined.
import re
import shlex
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


KUBE_BENCH_IMAGE = 'docker.io/aquasec/kube-bench:v0.10.6'
HOST_PATHS = [('var-lib-etcd', '/var/lib/etcd', '/var/lib/etcd'), ('var-lib-kubelet', '/var/lib/kubelet', '/var/lib/kubelet'),
              ('etc-systemd', '/etc/systemd', '/etc/systemd'), ('etc-kubernetes', '/etc/kubernetes', '/etc/kubernetes'),
              ('usr-bin', '/usr/bin', '/usr/local/mount-from-host/bin')]


def run_with_limit(arguments, limit, text_input=None):
    return subprocess.run(arguments, capture_output=True, text=True, timeout=limit, input=text_input)


def finished_log(kind, name, condition):
    waited = run_with_limit(['kubectl', '-n', NAMESPACE, 'wait', condition, kind + '/' + name, '--timeout=150s'], 170)
    assert waited.returncode == 0, 'The grader ' + kind + ' ' + name + ' did not finish'
    return run_with_limit(['kubectl', '-n', NAMESPACE, 'logs', kind + '/' + name], 30).stdout


def image_output(name, script):
    """Run a shell script in a short pod with the kube-bench image."""
    run_with_limit(['kubectl', '-n', NAMESPACE, 'delete', 'pod', name, '--ignore-not-found', '--wait=true'], 60)
    started = run_with_limit(['kubectl', '-n', NAMESPACE, 'run', name, '--restart=Never', '--image-pull-policy=IfNotPresent',
                              '--image=' + KUBE_BENCH_IMAGE, '--command', '--', 'sh', '-c', script], 30)
    assert started.returncode == 0, 'Could not start the grader pod'
    try:
        return finished_log('pod', name, "--for=jsonpath={.status.phase}=Succeeded")
    finally:
        run_with_limit(['kubectl', '-n', NAMESPACE, 'delete', 'pod', name, '--ignore-not-found', '--wait=false'], 30)


def bench_job(name, arguments):
    """Run kube-bench as a Job on the control plane node and return its log."""
    container = {'name': 'kube-bench', 'image': KUBE_BENCH_IMAGE, 'imagePullPolicy': 'IfNotPresent',
                 'command': ['kube-bench', 'run'] + arguments,
                 'volumeMounts': [{'name': item[0], 'mountPath': item[2], 'readOnly': True} for item in HOST_PATHS]}
    spec = {'hostPID': True, 'restartPolicy': 'Never', 'containers': [container],
            'nodeSelector': {'node-role.kubernetes.io/control-plane': ''},
            'tolerations': [{'key': 'node-role.kubernetes.io/control-plane', 'operator': 'Exists', 'effect': 'NoSchedule'}],
            'volumes': [{'name': item[0], 'hostPath': {'path': item[1]}} for item in HOST_PATHS]}
    job = {'apiVersion': 'batch/v1', 'kind': 'Job', 'metadata': {'name': name, 'namespace': NAMESPACE},
           'spec': {'backoffLimit': 0, 'template': {'spec': spec}}}
    run_with_limit(['kubectl', '-n', NAMESPACE, 'delete', 'job', name, '--ignore-not-found', '--wait=true'], 60)
    applied = run_with_limit(['kubectl', 'apply', '-f', '-'], 30, json.dumps(job))
    assert applied.returncode == 0, 'Could not start the grader Job'
    try:
        return finished_log('job', name, '--for=condition=complete')
    finally:
        run_with_limit(['kubectl', '-n', NAMESPACE, 'delete', 'job', name, '--ignore-not-found', '--wait=false'], 30)


def learner_job(name):
    """Return the Job, its pod and its log after checking that it completed."""
    job = get('job', name)
    assert job.get('status', {}).get('succeeded', 0) >= 1, 'The Job ' + name + ' has not completed'
    pods = json.loads(kubectl('-n', NAMESPACE, 'get', 'pods', '-l', 'job-name=' + name, '-o', 'json'))['items']
    finished = [pod for pod in pods if pod['status'].get('phase') == 'Succeeded']
    assert finished, 'The Job ' + name + ' has no finished pod'
    log = run_with_limit(['kubectl', '-n', NAMESPACE, 'logs', 'pod/' + finished[0]['metadata']['name']], 30).stdout
    return job, finished[0], log


def command_line(pod_spec):
    """The words of the container command, with a "sh -c" script split into words."""
    container = pod_spec['containers'][0]
    words = container.get('command', []) + container.get('args', [])
    if len(words) >= 3 and words[0].split('/')[-1] in ('sh', 'bash', 'ash') and words[1] == '-c':
        words = shlex.split(words[2])
    return words


def option(arguments, name):
    """The value of an option given as --name value or --name=value."""
    value = None
    for index, item in enumerate(arguments):
        if item == '--' + name and index + 1 < len(arguments):
            value = arguments[index + 1]
        elif item.startswith('--' + name + '='):
            value = item.split('=', 1)[1]
    return value

job, pod, log = learner_job('master-audit')
assert option(command_line(pod['spec']), 'targets') == 'master', 'Run kube-bench with --targets master'
saved = get('configmap', 'master-result').get('data', {})
if wants('totals-match'):
    totals = {}
    for number, state in re.findall(r'^(\d+) checks (PASS|FAIL|WARN|INFO)$', log, re.M):
        totals[state.lower()] = number
    assert len(totals) == 4, 'The log of master-audit has no summary'
    for key, number in totals.items():
        assert saved.get(key, '').strip() == number, 'The key ' + key + ' differs from the summary of the report'
if wants('section-counts-match'):
    for section in ('1.1', '1.2'):
        expected = len(re.findall(r'^\[FAIL\] ' + re.escape(section) + r'\.\d+', log, re.M))
        assert saved.get('fail-' + section, '').strip() == str(expected), 'The key fail-' + section + ' differs from the report'
