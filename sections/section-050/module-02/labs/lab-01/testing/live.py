R = '/var/lib/training-release/k8s/lab'


def node_sh(script, success=True):
    return node_exec(NODE, 'sh', '-c', script, success=success)


failing = [
    tool for tool in ('kubectl', 'kubeadm', 'kubelet')
    if node_sh("cat %s/%s.sha256" % (R, tool)).stdout.strip()
    != node_sh("sha256sum '%s/%s' | cut -d' ' -f1" % (R, tool)).stdout.strip()
]
assert len(failing) == 1, 'The staged files were changed: exactly one binary must fail verification'
if wants('failing-binary'):
    result = node_sh("cat %s/result.txt" % R, success=False)
    assert result.returncode == 0, 'Write the result file %s/result.txt on the control plane node' % R
    assert result.stdout.strip() == failing[0], 'The result file does not name the binary that fails verification'
