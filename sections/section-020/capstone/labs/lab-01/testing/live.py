import json as _json, base64 as _b64
node=get('node',WORKER,namespace=None)
assert any(c['type']=='Ready' and c['status']=='True' for c in node['status']['conditions']), 'The worker node must stay Ready'
if wants('api-profiling') or wants('secret-encryption'):
    pod=get('pod','kube-apiserver-'+NODE,namespace='kube-system')
if wants('api-profiling'):
    assert '--profiling=false' in pod['spec']['containers'][0]['command'], 'Disable API server profiling'
if wants('etcd-data-dir'):
    assert node_exec(NODE,'stat','-c','%a','/var/lib/etcd').stdout.strip() == '700', 'Set mode 700 on the etcd data directory'
if wants('secret-encryption'):
    assert '--encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml' in pod['spec']['containers'][0]['command'], 'Set the encryption provider configuration flag'
    stored=subprocess.run(['kubectl','-n','kube-system','exec','etcd-'+NODE,'--','etcdctl','--endpoints=https://127.0.0.1:2379','--cacert=/etc/kubernetes/pki/etcd/ca.crt','--cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt','--key=/etc/kubernetes/pki/etcd/healthcheck-client.key','get','/registry/secrets/starfleet/launch-code','--print-value-only'],capture_output=True,timeout=30)
    assert stored.returncode == 0, 'Could not read the Secret from etcd'
    assert b'k8s:enc:aescbc:v1:' in stored.stdout, 'The Secret is not stored with the aescbc provider'
    assert b'warp-nine-launch' not in stored.stdout, 'The Secret is still readable in etcd'
    encoded = kubectl('-n', 'starfleet', 'get', 'secret', 'launch-code', '-o', 'jsonpath={.data.code}')
    assert _b64.b64decode(encoded) == b'warp-nine-launch', 'The API no longer returns the Secret value'
if wants('kubelet-hardening'):
    cfg=_json.loads(kubectl('get','--raw','/api/v1/nodes/'+WORKER+'/proxy/configz'))['kubeletconfig']
    assert cfg['authentication']['anonymous']['enabled'] is False, 'Disable anonymous kubelet authentication'
    assert cfg['authorization']['mode'] == 'Webhook', 'Set the kubelet authorization mode to Webhook'
    assert cfg.get('readOnlyPort', 0) == 0, 'Close the kubelet read-only port'
if wants('cis-evidence'):
    evidence=get('configmap','cis-evidence')['data']
    for key in ('apiserver-profiling','etcd-data-dir','etcd-encryption','kubelet-anonymous-auth','kubelet-authorization-mode','kubelet-read-only-port'):
        assert evidence.get(key) == 'fixed', 'Set ' + key + ' to fixed in the evidence ConfigMap'
    assert evidence.get('before','').strip() and evidence.get('after','').strip() and evidence['before'] != evidence['after'], 'Record different non-empty before and after text'
