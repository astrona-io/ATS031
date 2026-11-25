import os

repository = '/var/lib/fleet-apt'
signed = node_exec(NODE, 'gpgv', '--keyring', repository + '/fleet-archive.gpg', repository + '/Release.gpg',
                   repository + '/Release', success=False).returncode == 0
assert signed, 'The signed Release file was changed; start the lab again'
release_digest = node_exec(NODE, 'sed', '-n', 's/^ \\([0-9a-f]\\{64\\}\\) [0-9]* Packages$/\\1/p', repository + '/Release').stdout.strip()
assert release_digest == node_exec(NODE, 'sha256sum', repository + '/Packages').stdout.split()[0], \
    'The Packages index was changed; start the lab again'
bad_packages = []
for stanza in node_exec(NODE, 'cat', repository + '/Packages').stdout.split('\n\n'):
    fields = dict(line.split(': ', 1) for line in stanza.splitlines() if ': ' in line and not line.startswith(' '))
    if 'Filename' not in fields:
        continue
    actual = node_exec(NODE, 'sha256sum', f"{repository}/{fields['Filename']}").stdout.split()[0]
    if actual != fields['SHA256']:
        bad_packages.append(os.path.basename(fields['Filename']))
assert len(bad_packages) == 1, 'The package pool was changed; start the lab again'
changed_files = [line.split()[-1] for line in node_exec(NODE, 'dpkg', '--verify', 'fleet-tools', success=False).stdout.splitlines()
                 if len(line) > 2 and line[2] == '5']
assert len(changed_files) == 1, 'The installed fleet-tools files were changed; start the lab again'


def review():
    found = command(['kubectl', '-n', NAMESPACE, 'get', 'configmap', 'repository-review', '-o', 'json'], success=False)
    assert found.returncode == 0, 'Create the ConfigMap repository-review in ' + NAMESPACE
    return json.loads(found.stdout).get('data') or {}


if wants('bad-package'):
    recorded = os.path.basename(review().get('bad-package', '').strip())
    assert recorded == bad_packages[0], 'bad-package must name the .deb file whose digest differs from the signed Packages index'
if wants('changed-file'):
    assert review().get('changed-file', '').strip() == changed_files[0], 'changed-file must be the full path that dpkg reports as changed'
