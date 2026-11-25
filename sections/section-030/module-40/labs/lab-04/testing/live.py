# Live checks: Python run inside the probe Pod against the Traefik Service.
# HELPERS is shared by every check; live() runs one check and reports the
# first failed assertion. Host name checks read only the Subject Alternative
# Name (SAN): a certificate with a Common Name (CN) and no SAN fails.
import base64

HELPERS = r"""
import base64, json, os, socket, ssl, sys, tempfile, time

TRAEFIK = 'traefik.ingress-system.svc'
FOOTER = '-----END CERTIFICATE-----'

def trust(pem):
    context = ssl.create_default_context(cadata=pem)
    context.verify_flags &= ~ssl.VERIFY_X509_STRICT
    context.hostname_checks_common_name = False
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

def write(text):
    handle = tempfile.NamedTemporaryFile('w', suffix='.pem', delete=False)
    handle.write(text)
    handle.close()
    return handle.name

def https_get(host, pem, path='/', sni=None, maximum=None, client=None):
    context = trust(pem)
    if maximum is not None:
        context.maximum_version = maximum
    if client is not None:
        certificate_path, key_path = write(client[0]), write(client[1])
        try:
            context.load_cert_chain(certificate_path, key_path)
        finally:
            os.unlink(certificate_path)
            os.unlink(key_path)
    raw = socket.create_connection((TRAEFIK, 443), timeout=5)
    with context.wrap_socket(raw, server_hostname=sni or host) as stream:
        return exchange(stream, host, path)

def unverified_get(host, path='/'):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    raw = socket.create_connection((TRAEFIK, 443), timeout=5)
    with context.wrap_socket(raw, server_hostname=host) as stream:
        return exchange(stream, host, path)

def http_get(host, path='/', port=80):
    raw = socket.create_connection((TRAEFIK, port), timeout=5)
    try:
        return exchange(raw, host, path)
    finally:
        raw.close()

def refused(call):
    try:
        call()
    except (ssl.SSLError, ConnectionResetError, BrokenPipeError):
        return True
    return False

pems = [base64.b64decode(argument).decode() for argument in sys.argv[1:]]

def status_of(response):
    return response.split('\r\n')[0]

def code_of(response):
    parts = status_of(response).split(' ')
    return parts[1] if len(parts) > 1 else ''

def header(response, name):
    for line in response.split('\r\n\r\n')[0].split('\r\n')[1:]:
        key, _, value = line.partition(':')
        if key.strip().lower() == name.lower():
            return value.strip()
    return None

def answer(host, pem, **options):
    try:
        return https_get(host, pem, **options)
    except (ssl.SSLError, OSError) as error:
        raise AssertionError('https://%s did not complete a verified TLS handshake: %s' % (host, getattr(error, 'reason', None) or error))

def first(pem):
    assert FOOTER in pem, 'The value is not a PEM certificate'
    return pem[:pem.index(FOOTER) + len(FOOTER)] + '\n'

def der(pem):
    return ssl.PEM_cert_to_DER_cert(first(pem))

def served(sni):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    raw = socket.create_connection((TRAEFIK, 443), timeout=5)
    with context.wrap_socket(raw, server_hostname=sni) as stream:
        return stream.getpeercert(binary_form=True)

def decode(pem):
    path = write(first(pem))
    try:
        return ssl._ssl._test_decode_cert(path)
    finally:
        os.unlink(path)

def dns_names(pem):
    return sorted(value for kind, value in decode(pem).get('subjectAltName', ()) if kind == 'DNS')

def days_left(pem):
    return (ssl.cert_time_to_seconds(decode(pem)['notAfter']) - time.time()) / 86400

def key_matches(pem, key):
    certificate_path, key_path = write(pem), write(key)
    try:
        ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER).load_cert_chain(certificate_path, key_path)
        return True
    except ssl.SSLError:
        return False
    finally:
        os.unlink(certificate_path)
        os.unlink(key_path)
"""


def live(body, values=()):
    result = command(['kubectl', '-n', NAMESPACE, 'exec', 'deployment/probe', '--', 'python', '-c',
                      HELPERS + body + "\nprint('verified')\n", *values], success=False)
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


def tls_secret(secret, namespace=NAMESPACE):
    """The base64 tls.crt and tls.key of a Secret of type kubernetes.io/tls."""
    resource = get('secret', secret, namespace)
    assert resource.get('type') == 'kubernetes.io/tls', 'The Secret ' + secret + ' must have the type kubernetes.io/tls'
    data = resource.get('data') or {}
    assert data.get('tls.crt') and data.get('tls.key'), 'The Secret ' + secret + ' must hold tls.crt and tls.key'
    return [data['tls.crt'], data['tls.key']]


def routes(ingress):
    """Every (host, path, pathType, Service, port) of an Ingress, in any order."""
    found = set()
    for rule in ingress['spec'].get('rules') or []:
        for item in (rule.get('http') or {}).get('paths') or []:
            service = (item.get('backend') or {}).get('service') or {}
            port = service.get('port') or {}
            found.add((rule.get('host'), item.get('path'), item.get('pathType'), service.get('name'), port.get('number', port.get('name'))))
    return found


def tls_entries(ingress):
    """Every spec.tls entry as (sorted hosts, secretName), in any order."""
    return {(tuple(sorted(entry.get('hosts') or [])), entry.get('secretName')) for entry in ingress['spec'].get('tls') or []}


def annotation(ingress, name):
    return (ingress['metadata'].get('annotations') or {}).get('traefik.ingress.kubernetes.io/' + name)


def can_i(*args):
    """kubectl auth can-i for the Traefik ServiceAccount: 'yes' or 'no'."""
    result = command(['kubectl', 'auth', 'can-i', *args, '--as=system:serviceaccount:ingress-system:traefik'], success=False)
    return result.stdout.strip()


def traefik_args():
    deployment = get('deployment', 'traefik', 'ingress-system')
    return deployment['spec']['template']['spec']['containers'][0].get('args') or []

if wants('api-closed'):
    assert not [item for item in traefik_args() if item.startswith('--api.insecure') and not item.endswith('=false')], \
        'Traefik must run without --api.insecure'
    container = get('deployment', 'traefik', 'ingress-system')['spec']['template']['spec']['containers'][0]
    assert all(port.get('containerPort') != 8080 for port in container.get('ports') or []), 'The Deployment traefik must not declare the container port 8080'
    ports = get('service', 'traefik', 'ingress-system')['spec'].get('ports') or []
    assert all(port.get('port') != 8080 for port in ports), 'The Service traefik must not publish port 8080'
    live(r"""
try:
    socket.create_connection((TRAEFIK, 8080), timeout=3).close()
    reachable = True
except OSError:
    reachable = False
assert not reachable, 'Port 8080 of the Traefik Service must not accept connections'
""")
if wants('secret-scope'):
    assert '--providers.kubernetesingress.namespaces=' + NAMESPACE in traefik_args(), \
        'Traefik must have the argument --providers.kubernetesingress.namespaces=' + NAMESPACE
    assert can_i('get', 'secrets', '-n', 'kube-system') == 'no', 'The Traefik ServiceAccount must not read Secrets in kube-system'
    assert can_i('list', 'secrets', '--all-namespaces') == 'no', 'The Traefik ServiceAccount must not list Secrets in every namespace'
    for verb in ('get', 'list', 'watch'):
        assert can_i(verb, 'secrets', '-n', NAMESPACE) == 'yes', 'The Traefik ServiceAccount must be allowed to ' + verb + ' Secrets in ' + NAMESPACE
    live(r"""
pem = pems[0]
assert served('dock.example.test') == der(pem), 'Traefik must still serve the dock-tls certificate for dock.example.test'
response = answer('dock.example.test', pem)
assert ' 200 ' in status_of(response) + ' ' and 'app=dock ' in response, 'https://dock.example.test must answer 200 from the Service dock'
""", [certificate('dock-tls')])
