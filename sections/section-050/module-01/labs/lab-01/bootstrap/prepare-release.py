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

node('mkdir','-p','/var/lib/training-release')
node('cp','/usr/bin/kubectl','/var/lib/training-release/kubectl')
node('sh','-c','cp /var/lib/training-release/kubectl /var/lib/training-release/kubectl-tampered; printf altered >> /var/lib/training-release/kubectl-tampered')
node('openssl','genpkey','-algorithm','RSA','-pkeyopt','rsa_keygen_bits:2048','-out','/var/lib/training-release/publisher.key')
node('openssl','pkey','-in','/var/lib/training-release/publisher.key','-pubout','-out','/var/lib/training-release/publisher.pub')
node('sh','-c','sha256sum /var/lib/training-release/kubectl > /var/lib/training-release/checksums.txt')
node('openssl','dgst','-sha256','-sign','/var/lib/training-release/publisher.key','-out','/var/lib/training-release/checksums.sig','/var/lib/training-release/checksums.txt')
node('rm','/var/lib/training-release/publisher.key')

