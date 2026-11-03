import json,subprocess,tempfile,base64,os
from pathlib import Path
CONTEXT="kind-astro-ats-031-capstone-020"
NODE="astro-ats-031-capstone-020-control-plane"
def run(*args):
    result=subprocess.run(args,check=True,text=True,capture_output=True,timeout=30)
    return result.stdout.strip()
assert run('kubectl','config','current-context')==CONTEXT, 'Select the private environment'
assert run('podman','inspect',NODE,'--format','{{index .Config.Labels "io.x-k8s.kind.cluster"}}')=='astro-ats-031-capstone-020', 'Refusing an unrelated node container'
def node(*args):return run('podman','exec',NODE,*args)
def put(path,content):
    with tempfile.TemporaryDirectory(prefix='training-node-') as temporary:
        source=Path(temporary)/'content';source.write_text(content)
        run('podman','cp',str(source),NODE+':'+path)
def api_manifest():
    with tempfile.TemporaryDirectory(prefix='training-api-') as temporary:
        source=Path(temporary)/'pod.yaml';source.write_text(node('cat','/etc/kubernetes/manifests/kube-apiserver.yaml'))
        return json.loads(run('kubectl','create','--dry-run=client','--validate=false','-f',str(source),'-o','json'))
def install_api_manifest(manifest):
    put('/etc/kubernetes/lab-api-pod.json',json.dumps(manifest))
    node('mv','/etc/kubernetes/lab-api-pod.json','/etc/kubernetes/manifests/kube-apiserver.yaml')
def set_api_flag(manifest,flag,value):
    container=manifest['spec']['containers'][0]
    container['command']=[arg for arg in container['command'] if not arg.startswith('--'+flag+'=')]+['--'+flag+'='+value]

def enable_encryption(manifest):
    key=base64.b64encode(os.urandom(32)).decode()
    config='apiVersion: apiserver.config.k8s.io/v1\nkind: EncryptionConfiguration\nresources:\n  - resources:\n      - secrets\n    providers:\n      - aescbc:\n          keys:\n            - name: key1\n              secret: '+key+'\n      - identity: {}\n'
    node('mkdir','-p','/etc/kubernetes/enc')
    put('/etc/kubernetes/enc/encryption-config.yaml',config)
    node('chmod','600','/etc/kubernetes/enc/encryption-config.yaml')
    set_api_flag(manifest,'encryption-provider-config','/etc/kubernetes/enc/encryption-config.yaml')
    spec=manifest['spec']; container=spec['containers'][0]
    container.setdefault('volumeMounts',[]).append({'name':'enc','mountPath':'/etc/kubernetes/enc','readOnly':True})
    spec.setdefault('volumes',[]).append({'name':'enc','hostPath':{'path':'/etc/kubernetes/enc','type':'DirectoryOrCreate'}})

manifest=api_manifest()
set_api_flag(manifest,'profiling','false')
enable_encryption(manifest)
install_api_manifest(manifest)
