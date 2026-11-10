import json,os,subprocess,tempfile
from pathlib import Path
import sys
CONTEXT = os.environ.get('ASTRONA_KUBE_CONTEXT') or 'kind-astro-ats-031-lab-050-01-01'
if subprocess.run(['kubectl', 'config', 'current-context'], capture_output=True, text=True).stdout.strip() != CONTEXT:
    sys.exit('Refusing to operate on another Kubernetes context')
CLUSTER=os.environ.get('ASTRONA_KIND_CLUSTER') or 'astro-ats-031-lab-050-01-01'
ENGINE=os.environ.get('ASTRONA_CONTAINER_ENGINE') or 'podman'
NODE=CLUSTER+'-control-plane'
def run(*args):
    result=subprocess.run(args,check=True,text=True,capture_output=True,timeout=30)
    return result.stdout.strip()
assert run(ENGINE,'inspect',NODE,'--format','{{index .Config.Labels "io.x-k8s.kind.cluster"}}')==CLUSTER, 'Refusing an unrelated node container'
def node(*args):return run(ENGINE,'exec',NODE,*args)

node('openssl','dgst','-sha256','-verify','/var/lib/training-release/publisher.pub','-signature','/var/lib/training-release/checksums.sig','/var/lib/training-release/checksums.txt')
trusted=node('cat','/var/lib/training-release/checksums.txt').split()[0]
actual=node('sha256sum','/var/lib/training-release/kubectl').split()[0]
changed=node('sha256sum','/var/lib/training-release/kubectl-tampered').split()[0]
assert trusted==actual and trusted!=changed
report_name='artifact-review';report={'result':'verified','tampered':'rejected','sha256':actual}

with tempfile.TemporaryDirectory(prefix='training-report-') as temporary:
    source=Path(temporary)/'configmap-report.json'
    source.write_text(json.dumps({'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':report_name,'namespace':'starfleet-031-050-01-01'},'data':report}))
    run('kubectl','apply','-f',str(source))

