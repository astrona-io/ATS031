node='astro-ats-031-playground-050-01-control-plane'
engine=__import__('os').environ.get('ASTRONA_CONTAINER_ENGINE') or 'podman'
command([engine,'exec',node,'openssl','dgst','-sha256','-verify','/var/lib/training-release/publisher.pub','-signature','/var/lib/training-release/checksums.sig','/var/lib/training-release/checksums.txt'])
trusted=command([engine,'exec',node,'cat','/var/lib/training-release/checksums.txt']).stdout.split()[0]
actual=command([engine,'exec',node,'sha256sum','/var/lib/training-release/kubectl']).stdout.split()[0]
changed=command([engine,'exec',node,'sha256sum','/var/lib/training-release/kubectl-tampered']).stdout.split()[0]
assert get('configmap','artifact-review')['data']['sha256']==trusted==actual and changed!=trusted, 'Bind the review to verified bytes'
