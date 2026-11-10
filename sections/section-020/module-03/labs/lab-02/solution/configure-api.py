import os,json,subprocess,tempfile
from pathlib import Path
import sys
CONTEXT = os.environ.get('ASTRONA_KUBE_CONTEXT') or 'kind-astro-ats-031-lab-020-03-02'
if subprocess.run(['kubectl', 'config', 'current-context'], capture_output=True, text=True).stdout.strip() != CONTEXT:
    sys.exit('Refusing to operate on another Kubernetes context')
CLUSTER=os.environ.get('ASTRONA_KIND_CLUSTER') or "astro-ats-031-lab-020-03-02"
ENGINE=os.environ.get('ASTRONA_CONTAINER_ENGINE') or 'podman'
NODE=CLUSTER+"-control-plane"
def run(*args):
    result=subprocess.run(args,check=True,text=True,capture_output=True,timeout=30)
    return result.stdout.strip()
assert run(ENGINE,'inspect',NODE,'--format','{{index .Config.Labels "io.x-k8s.kind.cluster"}}')==CLUSTER, 'Refusing an unrelated node container'
def node(*args):return run(ENGINE,'exec',NODE,*args)
def put(path,content):
    with tempfile.TemporaryDirectory(prefix='training-node-') as temporary:
        source=Path(temporary)/'content';source.write_text(content)
        run(ENGINE,'cp',str(source),NODE+':'+path)
def api_manifest():
    with tempfile.TemporaryDirectory(prefix='training-api-') as temporary:
        source=Path(temporary)/'pod.yaml';source.write_text(node('cat','/etc/kubernetes/manifests/kube-apiserver.yaml'))
        return json.loads(run('kubectl','create','--dry-run=client','--validate=false','-f',str(source),'-o','json'))
def install_api_manifest(manifest):
    put('/etc/kubernetes/lab-api-pod.json',json.dumps(manifest))
    node('mv','/etc/kubernetes/lab-api-pod.json','/etc/kubernetes/manifests/kube-apiserver.yaml')
def set_api_flag(container,flag,value):
    container['command']=[arg for arg in container['command'] if not arg.startswith('--'+flag+'=')]+['--'+flag+'='+value]

manifest=api_manifest(); container=manifest['spec']['containers'][0]
set_api_flag(container,'profiling','false')
install_api_manifest(manifest)
node('chown','root:root','/etc/kubernetes/manifests/kube-apiserver.yaml')
node('chmod','600','/etc/kubernetes/manifests/kube-apiserver.yaml')
