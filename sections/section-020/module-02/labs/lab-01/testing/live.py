# Run kube-bench again for the master target and compare its failing 1.2.x checks
# with the list that the learner saved. The Job is removed afterwards.
import re

def _kubectl_raw(args, timeout):
    return subprocess.run(['kubectl', *args], capture_output=True, text=True, timeout=timeout)

def _failing_ids_now():
    _kubectl_raw(['-n', 'default', 'delete', 'job', 'kube-bench-verify', '--ignore-not-found', '--wait=true'], 60)
    applied = _kubectl_raw(['apply', '-f', str(DIRECTORY / 'verify-job.yaml')], 30)
    assert applied.returncode == 0, 'Could not start the verification Job'
    try:
        waited = _kubectl_raw(['-n', 'default', 'wait', '--for=condition=complete', 'job/kube-bench-verify', '--timeout=150s'], 170)
        assert waited.returncode == 0, 'The verification Job did not complete'
        logs = _kubectl_raw(['-n', 'default', 'logs', 'job/kube-bench-verify'], 30).stdout
    finally:
        _kubectl_raw(['-n', 'default', 'delete', 'job', 'kube-bench-verify', '--ignore-not-found', '--wait=false'], 30)
    start = logs.find('{"')
    assert start >= 0, 'The verification Job printed no JSON'
    report, _ = json.JSONDecoder().raw_decode(logs[start:])
    found = set()
    def walk(node):
        if isinstance(node, dict):
            if 'test_number' in node and node.get('status') == 'FAIL':
                found.add(str(node['test_number']))
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
    walk(report)
    return {item for item in found if re.fullmatch(r'1\.2\.\d+', item)}

_saved = get('configmap', 'failing-checks')
_learner = {line.strip() for line in _saved.get('data', {}).get('ids', '').splitlines() if line.strip()}
assert _learner, 'The ConfigMap key ids is empty'
assert all(re.fullmatch(r'1\.2\.\d+', item) for item in _learner), 'The list may hold only 1.2.x check ids'
assert _learner == _failing_ids_now(), 'The saved list differs from the failing 1.2.x checks of the control plane'
