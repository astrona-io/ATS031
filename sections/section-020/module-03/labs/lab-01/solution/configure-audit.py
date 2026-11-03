import json,subprocess,tempfile
from pathlib import Path
CONTEXT="kind-astro-ats-031-lab-020-03-01"
NODE="astro-ats-031-lab-020-03-01-control-plane"
def run(*args):
    result=subprocess.run(args,check=True,text=True,capture_output=True,timeout=30)
    return result.stdout.strip()
assert run('kubectl','config','current-context')==CONTEXT, 'Select the private environment'
assert run('podman','inspect',NODE,'--format','{{index .Config.Labels "io.x-k8s.kind.cluster"}}')=='astro-ats-031-lab-020-03-01', 'Refusing an unrelated node container'
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
def set_api_flag(container,flag,value):
    container['command']=[arg for arg in container['command'] if not arg.startswith('--'+flag+'=')]+['--'+flag+'='+value]

node('mkdir','-p','/etc/kubernetes/policy','/var/log/kubernetes/audit')
node('cp','/opt/training/audit-policy.yaml','/etc/kubernetes/policy/audit-policy.yaml')
manifest=api_manifest(); container=manifest['spec']['containers'][0]
set_api_flag(container,'audit-policy-file','/etc/kubernetes/policy/audit-policy.yaml')
set_api_flag(container,'audit-log-path','/var/log/kubernetes/audit/audit.log')
set_api_flag(container,'audit-log-maxage','30')
set_api_flag(container,'audit-log-maxbackup','10')
set_api_flag(container,'audit-log-maxsize','100')
container.setdefault('volumeMounts',[]).extend([
    {'name':'audit-policy','mountPath':'/etc/kubernetes/policy','readOnly':True},
    {'name':'audit-log','mountPath':'/var/log/kubernetes/audit'}])
manifest['spec'].setdefault('volumes',[]).extend([
    {'name':'audit-policy','hostPath':{'path':'/etc/kubernetes/policy','type':'DirectoryOrCreate'}},
    {'name':'audit-log','hostPath':{'path':'/var/log/kubernetes/audit','type':'DirectoryOrCreate'}}])
install_api_manifest(manifest)
