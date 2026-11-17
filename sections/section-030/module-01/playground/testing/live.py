certificate=get('secret','probe-tls')['data']['tls.crt']
script=r"""import base64,socket,ssl,sys
context=ssl.create_default_context(cadata=base64.b64decode(sys.argv[1]).decode())
context.verify_flags &= ~ssl.VERIFY_X509_STRICT
with context.wrap_socket(socket.create_connection(('traefik.ingress-system.svc',443),timeout=5),server_hostname='probe.local') as stream:
    stream.sendall(b'GET / HTTP/1.1\r\nHost: probe.local\r\nConnection: close\r\n\r\n')
    response=b''
    while True:
        data=stream.recv(65536)
        if not data: break
        response+=data
    assert b'200 OK' in response and b'version=v1' in response
try:
    with context.wrap_socket(socket.create_connection(('traefik.ingress-system.svc',443),timeout=5),server_hostname='wrong.local'):
        raise AssertionError('Mismatched certificate unexpectedly accepted')
except ssl.SSLCertVerificationError:
    print('matching-response-and-mismatch-rejection')
"""
assert kubectl('-n','starfleet','exec','deployment/probe','--','python','-c',script,certificate)=='matching-response-and-mismatch-rejection', 'Verify TLS identity and response'
