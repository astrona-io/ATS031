def main():
    assert kubectl('config', 'current-context') == CONTEXT, 'Refusing to operate on another Kubernetes context'
    base = '/var/lib/training-release/k8s'
    names = node(CONTROL, "ls %s/release/v1.35.0/bin/linux/*/" % base).stdout
    assert 'kubectl.sha256' in names, 'The staged mirror is missing'
    current = '%s/current' % base
    for tool in ('kubectl', 'kubeadm', 'kubelet'):
        expected = node(CONTROL, 'cat %s/%s.sha256' % (current, tool)).stdout.strip()
        assert digest(CONTROL, '%s/%s' % (current, tool)) == expected, 'A genuine mirror file does not match its checksum file'
    expected = node(CONTROL, 'cat %s/downloads/kubeadm.sha256' % base).stdout.strip()
    assert digest(CONTROL, '%s/downloads/kubeadm' % base) != expected, 'The staged kubeadm download should be altered'
    print('Staged mirror verified')


if __name__ == '__main__':
    try:
        main()
    except (AssertionError, KeyError, ValueError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
