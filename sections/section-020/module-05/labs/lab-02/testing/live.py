import json as _json
def configz():
    return _json.loads(kubectl('get','--raw','/api/v1/nodes/'+WORKER+'/proxy/configz'))['kubeletconfig']
cfg=configz()
node=get('node',WORKER,namespace=None)
assert any(c['type']=='Ready' and c['status']=='True' for c in node['status']['conditions']), 'The worker node must stay Ready'
if wants('kubelet-file-modes'):
    assert node_exec(WORKER,'stat','-c','%a','/var/lib/kubelet/config.yaml').stdout.strip() == '600', 'Set mode 600 on /var/lib/kubelet/config.yaml'
    assert node_exec(WORKER,'stat','-c','%a','/etc/kubernetes/kubelet.conf').stdout.strip() == '600', 'Set mode 600 on /etc/kubernetes/kubelet.conf'
if wants('certificate-rotation'):
    assert cfg.get('rotateCertificates') is True, 'Enable kubelet certificate rotation'
if wants('streaming-idle-timeout'):
    assert cfg.get('streamingConnectionIdleTimeout') == '5m0s', 'Set streamingConnectionIdleTimeout to 5m'
if wants('tls-min-version'):
    assert cfg.get('tlsMinVersion') == 'VersionTLS12', 'Set tlsMinVersion to VersionTLS12'
