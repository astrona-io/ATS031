---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Disable API Server Profiling In A Private Node Solution

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-01-01" || exit 1
node_name="astro-ats-031-lab-020-01-01-control-plane"
worker_name="astro-ats-031-lab-020-01-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Inspect And Explain

The isolated environment has two healthy probe replicas, an internal Service and two client Pods. The required result has not been configured.

Inspect the current objects before changing them:

```sh
kubectl -n starfleet-031-020-01-01 get pods -o wide
kubectl get nodes -o wide
```

Set the isolated API server flag `--profiling=false`. Create ConfigMap `benchmark-review` recording `component: kube-apiserver`, `control: disable-profiling` and `result: corrected`. Keep the API ready and both application replicas available. This is one scoped configuration review, not a claim of full Center for Internet Security (CIS) benchmark compliance.

Save this as `configmap-benchmark-review.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: benchmark-review
  namespace: starfleet-031-020-01-01
data:
  component: kube-apiserver
  control: disable-profiling
  result: corrected
```

Save this as `configure-api.py`:

```python
import json,subprocess,tempfile
from pathlib import Path
CONTEXT="kind-astro-ats-031-lab-020-01-01"
NODE="astro-ats-031-lab-020-01-01-control-plane"
def run(*args):
    result=subprocess.run(args,check=True,text=True,capture_output=True,timeout=30)
    return result.stdout.strip()
assert run('kubectl','config','current-context')==CONTEXT, 'Select the private environment'
assert run('podman','inspect',NODE,'--format','{{index .Config.Labels "io.x-k8s.kind.cluster"}}')=='astro-ats-031-lab-020-01-01', 'Refusing an unrelated node container'
def node(*args):return run('podman','exec',NODE,*args)
def put(path,content):
    with tempfile.TemporaryDirectory(prefix='training-node-') as temporary:
        source=Path(temporary)/'content';source.write_text(content)
        run('podman','cp',str(source),NODE+':'+path)
def api_manifest():
    with tempfile.TemporaryDirectory(prefix='training-api-') as temporary:
        source=Path(temporary)/'pod.yaml';source.write_text(node('cat','/etc/kubernetes/manifests/kube-apiserver.yaml'))
        return json.loads(run('kubectl','create','--dry-run=client','--validate=false','-f',str(source),'-o','json'))
def set_api_flag(flag,value):
    manifest=api_manifest(); container=manifest['spec']['containers'][0]
    container['command']=[arg for arg in container['command'] if not arg.startswith('--'+flag+'=')]+['--'+flag+'='+value]
    put('/etc/kubernetes/lab-api-pod.json',json.dumps(manifest))
    node('mv','/etc/kubernetes/lab-api-pod.json','/etc/kubernetes/manifests/kube-apiserver.yaml')

set_api_flag('profiling','false')
```

Apply the scoped correction:

```sh
python3 configure-api.py
api_ready=0
for attempt in $(seq 1 80); do
  if kubectl --request-timeout=3s get --raw=/readyz >/dev/null 2>&1; then api_ready=1; break; fi
  sleep 3
done
test "$api_ready" -eq 1

kubectl apply -f configmap-benchmark-review.yaml
```

## Verify The Result

Observe the actual result. A denied request returns a nonzero status when the denial works, so run it separately from a shell sequence that stops on error. Status convergence and a successful request establish different parts of the result.

```sh
kubectl get --raw=/readyz
kubectl -n starfleet-031-020-01-01 exec shuttle -- wget -q -T 3 -O- http://probe/
```

Review and correct one effective control-plane setting while keeping API access available. The commands above deliberately target one environment. Keep its remaining components available so an unrelated failure cannot stand in for the required denial or correction. No example command output is presented as evidence of a completed run. A matching field alone does not establish that a process used it or that a controller reconciled it.

After recording your result, remove the independent lab with `astrona destroy ats-031-lab-020-01-01`.

## Common pitfalls

> [!WARNING]
> Use the version-appropriate benchmark and record the selected control. One corrected flag does not establish overall compliance. Backups belong outside the kubelet static-manifest directory.
