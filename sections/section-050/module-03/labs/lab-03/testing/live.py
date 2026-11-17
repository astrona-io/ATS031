RECORDS = '/var/lib/build-records'
APPROVAL = '/var/lib/approval'


def verify(directory, key, blob):
    return node_exec(NODE, 'cosign', 'verify-blob', '--key', f'{directory}/{key}', '--signature', f'{directory}/{blob}.sig',
                     '--insecure-ignore-tlog=true', f'{directory}/{blob}', success=False).returncode == 0


records = sorted(name for name in node_exec(NODE, 'ls', RECORDS).stdout.split() if name.endswith('.txt'))
assert len(records) == 6, 'The build records were changed; start the lab again'
rejected = {record for record in records if not verify(RECORDS, 'fleet.pub', record)}
assert 2 <= len(rejected) <= 3, 'The build records or signatures were changed; start the lab again'

if wants('rejected-records'):
    found = command(['kubectl', '-n', NAMESPACE, 'get', 'configmap', 'cosign-review', '-o', 'json'], success=False)
    assert found.returncode == 0, 'Create the ConfigMap cosign-review in ' + NAMESPACE
    recorded = (json.loads(found.stdout).get('data') or {}).get('rejected', '')
    assert set(recorded.replace(',', ' ').split()) == rejected, \
        'rejected must list exactly the build records that do not verify with fleet.pub'
if wants('signed-approval'):
    assert node_exec(NODE, 'test', '-f', APPROVAL + '/cosign.pub', success=False).returncode == 0, \
        'Generate a key pair in ' + APPROVAL + ' so that cosign.pub is there'
    fleet_key = node_exec(NODE, 'cat', RECORDS + '/fleet.pub').stdout
    assert node_exec(NODE, 'cat', APPROVAL + '/cosign.pub').stdout != fleet_key, 'cosign.pub must be a new key, not the fleet key'
    assert verify(APPROVAL, 'cosign.pub', 'approval.txt'), \
        'approval.txt.sig must be a signature of approval.txt that verifies with ' + APPROVAL + '/cosign.pub'
    assert node_exec(NODE, 'test', '-e', APPROVAL + '/cosign.key', success=False).returncode != 0, \
        'Delete the private key cosign.key after signing'
