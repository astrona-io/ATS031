import json,os,subprocess,tempfile
from pathlib import Path
CONTEXT="kind-astro-ats-031-playground-050-01"
NODE="astro-ats-031-playground-050-01-control-plane"
ENGINE=os.environ.get('ASTRONA_CONTAINER_ENGINE') or 'podman'
def run(*args):
    result=subprocess.run(args,check=True,text=True,capture_output=True,timeout=30)
    return result.stdout.strip()
assert run('kubectl','config','current-context')==CONTEXT, 'Select the private environment'
assert run(ENGINE,'inspect',NODE,'--format','{{index .Config.Labels "io.x-k8s.kind.cluster"}}')=='astro-ats-031-playground-050-01', 'Refusing an unrelated node container'
def node(*args):return run(ENGINE,'exec',NODE,*args)

node('mkdir','-p','/var/lib/training-release')
node('cp','/usr/bin/kubectl','/var/lib/training-release/kubectl')
node('sh','-c','cp /var/lib/training-release/kubectl /var/lib/training-release/kubectl-tampered; printf altered >> /var/lib/training-release/kubectl-tampered')
node('openssl','genpkey','-algorithm','RSA','-pkeyopt','rsa_keygen_bits:2048','-out','/var/lib/training-release/publisher.key')
node('openssl','pkey','-in','/var/lib/training-release/publisher.key','-pubout','-out','/var/lib/training-release/publisher.pub')
node('sh','-c','sha256sum /var/lib/training-release/kubectl > /var/lib/training-release/checksums.txt')
node('openssl','dgst','-sha256','-sign','/var/lib/training-release/publisher.key','-out','/var/lib/training-release/checksums.sig','/var/lib/training-release/checksums.txt')
node('rm','/var/lib/training-release/publisher.key')

