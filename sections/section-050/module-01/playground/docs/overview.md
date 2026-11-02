---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Guided Practice: Verify Signed Artifact Checksums

Use a host shell with the private kubeconfig for this module playground. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

<!-- astrona:playground:renew -->

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-playground-050-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-playground-050-01" || exit 1
node_name="astro-ats-031-playground-050-01-control-plane"
worker_name="astro-ats-031-playground-050-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Inspect And Explain

The isolated environment has two healthy probe replicas, an internal Service and two client Pods. The required result has not been configured.

Inspect the current objects before changing them:

```sh
kubectl -n starfleet get pods -o wide
kubectl get nodes -o wide
```

Use the public key provisioned with the isolated fixture to verify checksums.sig over checksums.txt. Verify the staged kubectl digest matches the authenticated manifest and the tampered copy does not. Record artifact-review with result verified, tampered rejected and the exact sha256. The fixture key is a local exercise trust root, not proof of the upstream Kubernetes publisher identity.

Save this as `configmap-artifact-review.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: artifact-review
  namespace: starfleet
data:
  result: verified
  tampered: rejected
```

Save this as `verify-release.py`:

```python
import json,subprocess,tempfile
from pathlib import Path
CONTEXT="kind-astro-ats-031-playground-050-01"
NODE="astro-ats-031-playground-050-01-control-plane"
def run(*args):
    result=subprocess.run(args,check=True,text=True,capture_output=True,timeout=30)
    return result.stdout.strip()
assert run('kubectl','config','current-context')==CONTEXT, 'Select the private environment'
assert run('podman','inspect',NODE,'--format','{{index .Config.Labels "io.x-k8s.kind.cluster"}}')=='astro-ats-031-playground-050-01', 'Refusing an unrelated node container'
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

```

Apply the scoped correction:

```sh
python3 verify-release.py
```

## Verify The Result

Observe the actual result. A denied request returns a nonzero status when the denial works, so run it separately from a shell sequence that stops on error. Status convergence and a successful request establish different parts of the result.

```sh
kubectl -n starfleet get configmaps
kubectl -n starfleet get deployment probe -o yaml
```

Verify a signed checksum manifest and reject altered bytes before using a binary. The commands above deliberately target one environment. Keep its remaining components available so an unrelated failure cannot stand in for the required denial or correction. No example command output is presented as evidence of a completed run. A matching field alone does not establish that a process used it or that a controller reconciled it.


## Common pitfalls

> [!WARNING]
> A checksum from an unauthenticated location does not establish publisher identity. Trust the provisioned exercise public key independently and verify the signed manifest before the bytes. Do not run the altered binary.
