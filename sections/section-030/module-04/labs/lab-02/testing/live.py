certificates = []
certificates = []
for ingress_name in ('alpha', 'bravo', 'charlie', 'delta'):
    certificates.append(get('secret', get('ingress', ingress_name)['spec']['tls'][0]['secretName'])['data']['tls.crt'])
script = r"""
import base64, socket, ssl, sys

TRAEFIK = 'traefik.ingress-system.svc'

def trust(pem):
    context = ssl.create_default_context(cadata=pem)
    context.verify_flags &= ~ssl.VERIFY_X509_STRICT
    return context

def exchange(stream, host, path='/'):
    stream.sendall(('GET %s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n' % (path, host)).encode())
    response = b''
    while True:
        data = stream.recv(65536)
        if not data:
            break
        response += data
    return response.decode(errors='replace')

def https_get(host, pem, path='/', sni=None, maximum=None):
    context = trust(pem)
    if maximum is not None:
        context.maximum_version = maximum
    raw = socket.create_connection((TRAEFIK, 443), timeout=5)
    with context.wrap_socket(raw, server_hostname=sni or host) as stream:
        return exchange(stream, host, path)

def http_get(host, path='/'):
    raw = socket.create_connection((TRAEFIK, 80), timeout=5)
    try:
        return exchange(raw, host, path)
    finally:
        raw.close()

def refused(call):
    try:
        call()
    except (ssl.SSLError, ConnectionResetError):
        return True
    return False

pems = [base64.b64decode(argument).decode() for argument in sys.argv[1:]]

def status_of(response):
    return response.split('\r\n')[0]

for host, pem in zip(('alpha', 'bravo', 'charlie', 'delta'), pems):
    name = host + '.example.test'
    response = https_get(name, pem)
    assert ' 200 ' in status_of(response) + ' ', 'Expected 200 for ' + name
    assert 'app=probe ' in response, 'Wrong backend for ' + name
    assert refused(lambda: https_get(name, pem, sni='wrong.example.test')), 'A wrong server name must be rejected for ' + name
print('verified')

"""
output = kubectl('-n', 'starfleet', 'exec', 'deployment/probe', '--', 'python', '-c', script, *certificates)
assert output == 'verified', 'Live verification failed: ' + output
