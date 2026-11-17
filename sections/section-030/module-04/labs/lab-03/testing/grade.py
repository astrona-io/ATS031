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

NS='rotation-training'
def check(outcome):
    active=get('secret','probe-tls',NS)['data']; target=get('secret','probe-next',NS)['data']; old=get('secret','probe-old',NS)['data']
    assert target['tls.crt']!=old['tls.crt'], 'Preserve the distinct replacement certificate'
    assert active['tls.crt']==target['tls.crt'] and active['tls.key']==target['tls.key'], 'Replace both fields of the active TLS Secret'
    if outcome=='replacement-secret': return
    if outcome!='served-certificate': raise RuntimeError('Unknown outcome')
    ca=get('configmap','rotation-trust',NS)['data']['ca.crt']
    code=r"""
import ssl,socket,base64,hashlib,sys
ctx=ssl.create_default_context(cadata=sys.argv[1])
with ctx.wrap_socket(socket.create_connection(('traefik.ingress-system.svc',443),timeout=4),server_hostname='probe.example.test') as stream:
 expected=ssl.PEM_cert_to_DER_cert(base64.b64decode(sys.argv[2]).decode())
 assert stream.getpeercert(binary_form=True)==expected, 'Fresh TLS connection still serves the previous certificate'
 stream.sendall(b'GET / HTTP/1.1\r\nHost: probe.example.test\r\nConnection: close\r\n\r\n')
 data=b''
 while True:
  chunk=stream.recv(65536)
  if not chunk: break
  data+=chunk
 assert b' 200 ' in data.split(b'\r\n')[0]+b' ' and b'app=probe ' in data, 'Preserve application routing'
 print('verified-rotation')
"""
    deadline=time.monotonic()+60
    while True:
        result=k('-n',NS,'exec','deployment/probe','--','python3','-c',code,ca,target['tls.crt'],ok=False)
        if result.returncode==0 and result.stdout.strip()=='verified-rotation': return
        if time.monotonic()>deadline: raise AssertionError('The live endpoint must serve the trusted replacement certificate and original application: '+result.stderr[-1000:])
        time.sleep(2)

if __name__ == '__main__':
    try:
        check(sys.argv[1])
    except AssertionError as error:
        print('FAIL:', error); sys.exit(1)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print('ERROR:', error); sys.exit(2)
    print('PASS:', sys.argv[1])
