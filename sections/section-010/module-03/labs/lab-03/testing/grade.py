import base64, json, os, pathlib, subprocess, sys, tempfile, time, uuid
def run(args,input=None,timeout=40):
    return subprocess.run(args,input=input,text=True,capture_output=True,timeout=timeout)
def k(*args,input=None,ok=True,timeout=40):
    result=run(['kubectl',*args],input=input,timeout=timeout)
    if ok and result.returncode: raise RuntimeError(result.stderr)
    return result
def get(kind,name,ns=None):
    result=k(*(['-n',ns] if ns else []),'get',kind,name,'--ignore-not-found','-o','json')
    assert result.stdout.strip(), 'Missing '+kind+' '+name
    return json.loads(result.stdout)
def apply(obj):
    return k('apply','-f','-',input=json.dumps(obj))
def delete(obj):
    k('delete','-f','-','--ignore-not-found','--wait=false',input=json.dumps(obj))

NS='ranges-training'
def connect(client,ip,port):
    code='import socket; s=socket.create_connection(("'+ip+'",'+str(port)+'),timeout=2); print(s.recv(80).decode());s.close()'
    result=k('-n',NS,'exec',client,'--','python3','-c',code,ok=False)
    if result.returncode and not any(e in result.stderr for e in ('TimeoutError','ConnectionRefusedError','timed out')): raise RuntimeError(result.stderr)
    return result.returncode==0 and 'range-service' in result.stdout
def check(outcome):
    for name in ('server','allowed','excluded'):
        p=get('pod',name,NS)
        if not any(c.get('type')=='Ready' and c.get('status')=='True' for c in p['status'].get('conditions',[])): raise RuntimeError(name+' must be healthy')
    ip=get('pod','server',NS)['status']['podIP']; excluded=get('pod','excluded',NS)['status']['podIP']
    policy=get('networkpolicy','bounded-range',NS)['spec']
    assert policy['podSelector']=={'matchLabels':{'app':'range-server'}}, 'Select the server only'
    rules=policy.get('ingress',[])
    assert any(peer.get('ipBlock')=={'cidr':'0.0.0.0/0','except':[excluded+'/32']} for rule in rules for peer in rule.get('from',[])), 'Use the excluded client address in ipBlock.except'
    assert any(p.get('port')==8080 and p.get('endPort')==8082 and p.get('protocol','TCP')=='TCP' for rule in rules for p in rule.get('ports',[])), 'Use a TCP endPort range from 8080 through 8082'
    for port in range(8079,8084):
        assert connect('server','127.0.0.1',port), 'Every server listener must stay healthy'
    if outcome=='address-exception':
        assert connect('allowed',ip,8081), 'The allowed client must reach the middle of the range'
        for port in (8080,8081,8082): assert not connect('excluded',ip,port), 'Reject the excluded client address'
    elif outcome=='port-range':
        for port in (8080,8081,8082): assert connect('allowed',ip,port), 'Allow every port inside the range'
        for port in (8079,8083): assert not connect('allowed',ip,port), 'Reject both neighboring ports'
    else: raise RuntimeError('Unknown outcome')

if __name__ == '__main__':
    try:
        check(sys.argv[1])
    except AssertionError as error:
        print('FAIL:', error); sys.exit(1)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print('ERROR:', error); sys.exit(2)
    print('PASS:', sys.argv[1])
