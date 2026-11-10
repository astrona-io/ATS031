LAB_FILES = '/var/lib/training-release/signed/lab'


def control_shell(script):
    return node_exec(NODE, 'sh', '-c', script, success=False)


gpg_ok = control_shell('cd %s && gpg --no-default-keyring --keyring ./publisher.gpg --verify gpg-notes.txt.asc gpg-notes.txt' % LAB_FILES).returncode == 0
cosign_ok = control_shell('cd %s && cosign verify-blob --key cosign.pub --signature cosign-notes.txt.sig --insecure-ignore-tlog=true cosign-notes.txt' % LAB_FILES).returncode == 0
assert gpg_ok != cosign_ok, 'Exactly one of the two signatures must fail; the staged files were changed or a tool is missing'
if wants('forged-signature'):
    result = control_shell('cat %s/result.txt' % LAB_FILES)
    assert result.returncode == 0, 'Write the result file %s/result.txt on the control plane node' % LAB_FILES
    assert result.stdout.strip() == ('cosign' if gpg_ok else 'gpg'), 'The result file does not name the forged signature'
