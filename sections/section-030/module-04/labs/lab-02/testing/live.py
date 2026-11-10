# Live checks: Python run inside the probe Pod against the Traefik Service.
# HELPERS is shared by every check; live() runs one check and reports the
# first failed assertion.
HELPERS = r"""
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

def answer(host, pem):
    try:
        return https_get(host, pem)
    except (ssl.SSLError, OSError) as error:
        raise AssertionError('https://%s did not complete a verified TLS handshake: %s' % (host, getattr(error, 'reason', None) or error))
"""


def live(body, certificates=()):
    result = command(['kubectl', '-n', NAMESPACE, 'exec', 'deployment/probe', '--', 'python', '-c',
                      HELPERS + body + "\nprint('verified')\n", *certificates], success=False)
    if result.returncode == 0 and result.stdout.strip() == 'verified':
        return
    lines = [line for line in (result.stderr + result.stdout).splitlines()
             if line.strip() and not line.startswith('command terminated with exit code')]
    raise AssertionError(lines[-1].removeprefix('AssertionError: ') if lines else 'Live check failed without output')


def certificate(secret):
    """The base64 tls.crt of a Secret in the lab namespace, or fail with a reason."""
    result = command(['kubectl', '-n', NAMESPACE, 'get', 'secret', secret, '-o', 'jsonpath={.data.tls\\.crt}'], success=False)
    assert result.returncode == 0 and result.stdout.strip(), 'The TLS Secret ' + secret + ' must exist with a certificate'
    return result.stdout.strip()

for host in ('alpha', 'bravo', 'charlie', 'delta'):
    if wants(host + '-ingress'):
        tls = get('ingress', host)['spec'].get('tls') or [{}]
        assert tls[0].get('secretName'), 'The Ingress ' + host + ' must name a TLS Secret'
        live('name = %r\n' % (host + '.example.test') + r"""
response = answer(name, pems[0])
assert ' 200 ' in status_of(response) + ' ', 'https://' + name + ' must answer 200 with the certificate of its Secret'
assert 'app=probe ' in response, 'https://' + name + ' must reach the Service probe'
assert refused(lambda: https_get(name, pems[0], sni='wrong.example.test')), 'A wrong server name must be rejected for ' + name
""", [certificate(tls[0]['secretName'])])
