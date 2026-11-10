import json as _json
def configz():
    return _json.loads(kubectl('get','--raw','/api/v1/nodes/'+WORKER+'/proxy/configz'))['kubeletconfig']
cfg=configz()
node=get('node',WORKER,namespace=None)
assert any(c['type']=='Ready' and c['status']=='True' for c in node['status']['conditions']), 'The worker node must stay Ready'
if wants('anonymous-auth'):
    assert cfg['authentication']['anonymous']['enabled'] is False, 'Disable anonymous kubelet authentication'
if wants('webhook-authorization'):
    assert cfg['authorization']['mode'] == 'Webhook', 'Set the kubelet authorization mode to Webhook'
if wants('read-only-port'):
    assert cfg.get('readOnlyPort', 0) == 0, 'Close the kubelet read-only port'
