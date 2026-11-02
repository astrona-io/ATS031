pod=get('pod','kube-apiserver-astro-ats-031-lab-020-01-01-control-plane',namespace='kube-system')
assert '--profiling=false' in pod['spec']['containers'][0]['command'], 'Disable the effective API profiling flag'
