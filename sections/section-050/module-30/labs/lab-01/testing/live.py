import re

review_directory = '/var/lib/doc-review'
documents = ('flight-plan.txt', 'crew-roster.txt', 'fuel-report.txt', 'nav-update.txt', 'comms-schedule.txt', 'cargo-manifest.txt')
rejected = set()
fingerprints = set()
for document in documents:
    path = f'{review_directory}/{document}'
    result = node_exec(NODE, 'gpgv', '--keyring', review_directory + '/publisher.gpg', path + '.asc', path, success=False)
    if result.returncode == 0:
        fingerprints.update(re.findall(r'using \S+ key ([0-9A-F]{40})', result.stderr))
    else:
        rejected.add(document)
assert 2 <= len(rejected) <= 3 and len(fingerprints) == 1, 'The staged documents were changed; start the lab again'


def review():
    found = command(['kubectl', '-n', NAMESPACE, 'get', 'configmap', 'signature-review', '-o', 'json'], success=False)
    assert found.returncode == 0, 'Create the ConfigMap signature-review in ' + NAMESPACE
    return json.loads(found.stdout).get('data') or {}


def recorded_rejected():
    return set(re.split(r'[\s,]+', review().get('rejected', '').strip())) - {''}


if wants('rejected-files'):
    assert rejected <= recorded_rejected(), 'rejected must name every document without a good signature from the publisher key'
if wants('accepted-files'):
    recorded = recorded_rejected()
    assert recorded, 'rejected must name at least one document'
    assert recorded <= rejected, 'rejected must not name a document that has a good signature from the publisher key'
if wants('publisher-fingerprint'):
    recorded = re.sub(r'\s', '', review().get('fingerprint', '')).upper()
    assert recorded == next(iter(fingerprints)), 'fingerprint must be the full 40-character fingerprint of the publisher key'
