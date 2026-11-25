def main():
    assert kubectl('config', 'current-context') == CONTEXT, 'Refusing to operate on another Kubernetes context'
    listing = node(CONTROL, 'ls /var/lib/training-release/signed').stdout.split()
    assert 'NO-GPG' in listing or 'release-notes.txt.asc' in listing, 'GPG fixture or marker is missing'
    assert 'NO-COSIGN' in listing or 'build-record.txt.sig' in listing, 'cosign fixture or marker is missing'
    if 'release-notes.txt.asc' in listing:
        good = node(CONTROL, "cd /var/lib/training-release/signed && gpg --no-default-keyring --keyring ./publisher.gpg --verify release-notes.txt.asc release-notes.txt", check=False)
        assert good.returncode == 0, 'The genuine release notes should verify'
    if 'build-record.txt.sig' in listing:
        good = node(CONTROL, "cd /var/lib/training-release/signed && cosign verify-blob --key cosign.pub --signature build-record.txt.sig --insecure-ignore-tlog=true build-record.txt", check=False)
        assert good.returncode == 0, 'The genuine build record should verify'
    pods = json.loads(kubectl('-n', 'starfleet', 'get', 'pods', '-l', 'app=relay', '-o', 'json'))['items']
    assert len(pods) == 1, 'The relay Deployment should run one pod'
    print('Staged fixtures verified')


if __name__ == '__main__':
    try:
        main()
    except (AssertionError, KeyError, ValueError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
