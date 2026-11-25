import re
import subprocess

OUTPOST = 'outpost-031-050-03-05'
TAGGED = 'docker.io/library/python:3.13-alpine'
PINNED = TAGGED + '@sha256:' + '0123456789abcdef' * 4


def dry_run_pod(namespace, image, init_image=None):
    """Create a Pod with server-side dry run: admission runs, nothing is stored."""
    spec = {'containers': [{'name': 'main', 'image': PINNED if init_image else image}]}
    if init_image:
        spec['initContainers'] = [{'name': 'setup', 'image': init_image}]
    pod = {'apiVersion': 'v1', 'kind': 'Pod', 'metadata': {'name': 'digest-check', 'namespace': namespace}, 'spec': spec}
    return subprocess.run(['kubectl', 'create', '--dry-run=server', '-f', '-'], input=json.dumps(pod),
                          capture_output=True, text=True, timeout=20)


def denied_by_policy(result):
    return result.returncode != 0 and 'ValidatingAdmissionPolicy' in result.stderr


if wants('denies-tags'):
    assert denied_by_policy(dry_run_pod(NAMESPACE, TAGGED)), \
        'A Pod with the tag-only image ' + TAGGED + ' must be denied by a ValidatingAdmissionPolicy in ' + NAMESPACE
    assert denied_by_policy(dry_run_pod(NAMESPACE, None, init_image=TAGGED)), \
        'A Pod whose init container uses a tag-only image must be denied too'
if wants('allows-digests'):
    denial = dry_run_pod(NAMESPACE, TAGGED)
    assert denied_by_policy(denial), 'A Pod with the tag-only image ' + TAGGED + ' must be denied by a ValidatingAdmissionPolicy in ' + NAMESPACE
    binding_name = re.search(r"with binding '([^']+)'", denial.stderr)
    assert binding_name, 'The denial must name the ValidatingAdmissionPolicyBinding: ' + denial.stderr.strip()
    binding = get('validatingadmissionpolicybinding', binding_name.group(1), namespace=None)
    assert binding['spec'].get('validationActions') == ['Deny'], 'Bind the policy with validationActions: ["Deny"]'
    for image in (PINNED, 'docker.io/library/python@sha256:' + 'fedcba9876543210' * 4):
        result = dry_run_pod(NAMESPACE, image)
        assert result.returncode == 0, 'A Pod with the digest-pinned image ' + image + ' must be admitted: ' + result.stderr.strip()
    result = dry_run_pod(OUTPOST, TAGGED)
    assert result.returncode == 0, 'Pods in ' + OUTPOST + ' must not be affected by the policy: ' + result.stderr.strip()
