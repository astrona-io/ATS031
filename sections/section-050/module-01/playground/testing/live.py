import os
ENGINE=os.environ.get('ASTRONA_CONTAINER_ENGINE','podman')
node='astro-ats-031-playground-050-01-control-plane'
command([ENGINE,'exec',node,'openssl','dgst','-sha256','-verify','/var/lib/training-release/publisher.pub','-signature','/var/lib/training-release/checksums.sig','/var/lib/training-release/checksums.txt'])
trusted=command([ENGINE,'exec',node,'cat','/var/lib/training-release/checksums.txt']).stdout.split()[0]
actual=command([ENGINE,'exec',node,'sha256sum','/var/lib/training-release/kubectl']).stdout.split()[0]
changed=command([ENGINE,'exec',node,'sha256sum','/var/lib/training-release/kubectl-tampered']).stdout.split()[0]
assert get('configmap','artifact-review')['data']['sha256']==trusted==actual and changed!=trusted, 'Bind the review to verified bytes'
