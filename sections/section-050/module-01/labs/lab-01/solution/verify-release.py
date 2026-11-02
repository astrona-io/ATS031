import json,subprocess,tempfile
from pathlib import Path
CONTEXT="kind-astro-ats-031-lab-050-01-01"
NODE="astro-ats-031-lab-050-01-01-control-plane"
def run(*args):
    result=subprocess.run(args,check=True,text=True,capture_output=True,timeout=30)
    return result.stdout.strip()
assert run('kubectl','config','current-context')==CONTEXT, 'Select the private environment'
assert run('podman','inspect',NODE,'--format','{{index .Config.Labels "io.x-k8s.kind.cluster"}}')=='astro-ats-031-lab-050-01-01', 'Refusing an unrelated node container'
def node(*args):return run('podman','exec',NODE,*args)

node('openssl','dgst','-sha256','-verify','/var/lib/training-release/publisher.pub','-signature','/var/lib/training-release/checksums.sig','/var/lib/training-release/checksums.txt')
trusted=node('cat','/var/lib/training-release/checksums.txt').split()[0]
actual=node('sha256sum','/var/lib/training-release/kubectl').split()[0]
changed=node('sha256sum','/var/lib/training-release/kubectl-tampered').split()[0]
assert trusted==actual and trusted!=changed
report_name='artifact-review';report={'result':'verified','tampered':'rejected','sha256':actual}

with tempfile.TemporaryDirectory(prefix='training-report-') as temporary:
    source=Path(temporary)/'configmap-report.json'
    source.write_text(json.dumps({'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':report_name,'namespace':'starfleet'},'data':report}))
    run('kubectl','apply','-f',str(source))

