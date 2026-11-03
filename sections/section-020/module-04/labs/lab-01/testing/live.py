NODE='astro-ats-031-lab-020-04-01-control-plane'
pod=get('pod','kube-apiserver-'+NODE,namespace='kube-system')
assert '--encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml' in pod['spec']['containers'][0]['command'], 'Set the encryption provider configuration flag'
stored=subprocess.run(['kubectl','-n','kube-system','exec','etcd-'+NODE,'--','etcdctl','--endpoints=https://127.0.0.1:2379','--cacert=/etc/kubernetes/pki/etcd/ca.crt','--cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt','--key=/etc/kubernetes/pki/etcd/healthcheck-client.key','get','/registry/secrets/starfleet/launch-code','--print-value-only'],capture_output=True,timeout=30)
assert stored.returncode == 0, 'Could not read the Secret from etcd'
assert b'k8s:enc:aescbc:v1:' in stored.stdout, 'The Secret is not stored with the aescbc provider'
assert b'warp-nine-launch' not in stored.stdout, 'The Secret is still readable in etcd'
import base64
encoded = kubectl('-n', 'starfleet', 'get', 'secret', 'launch-code', '-o', 'jsonpath={.data.code}')
assert base64.b64decode(encoded) == b'warp-nine-launch', 'The API no longer returns the Secret value'
