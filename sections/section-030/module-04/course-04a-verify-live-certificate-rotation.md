---
draft: true
---
# Verify A Live Certificate Rotation

A TLS Secret can change before an ingress controller has loaded its new contents. Certificate rotation is complete only when a fresh connection receives the replacement certificate and still verifies the intended hostname and issuer. This independent lab stages an old and a replacement leaf certificate signed by the same training CA; it does not rotate the CA itself.

<!-- astrona:playground:renew -->

Inspect the route and Secret names without printing private key material:

```sh
kubectl -n rotation-training get ingress probe -o yaml
kubectl -n rotation-training get secrets probe-tls probe-next probe-old
```

Copy the staged certificate and key into the existing active Secret through a pipe:

```sh
kubectl -n rotation-training get secret probe-next -o json | python3 -c 'import json,sys; s=json.load(sys.stdin); print(json.dumps({"apiVersion":"v1","kind":"Secret","metadata":{"name":"probe-tls","namespace":"rotation-training"},"type":"kubernetes.io/tls","data":s["data"]}))' | kubectl apply -f -
```

Both fields change together. The Ingress keeps its `secretName: probe-tls`, and Traefik watches the Secret update. The command avoids persisting a second unprotected private-key file.

Read the trusted CA and compare certificate fingerprints from inside the cluster. Save this as `verify-rotation.py`:

```python
import base64, hashlib, json, subprocess

def read(kind, name):
    return json.loads(subprocess.check_output([
        'kubectl', '-n', 'rotation-training', 'get', kind, name, '-o', 'json']))['data']

ca = read('configmap', 'rotation-trust')['ca.crt']
expected = read('secret', 'probe-next')['tls.crt']
code = "import ssl,socket,base64,hashlib,sys\nctx=ssl.create_default_context(cadata=sys.argv[1])\nwith ctx.wrap_socket(socket.create_connection(('traefik.ingress-system.svc',443),timeout=5),server_hostname='probe.example.test') as s:\n actual=s.getpeercert(binary_form=True)\n expected=ssl.PEM_cert_to_DER_cert(base64.b64decode(sys.argv[2]).decode())\n assert actual==expected, 'Certificate has not rotated'\n print('SHA256',hashlib.sha256(actual).hexdigest())\n s.sendall(b'GET / HTTP/1.1\\r\\nHost: probe.example.test\\r\\nConnection: close\\r\\n\\r\\n')\n print(s.recv(4096).decode())"
subprocess.run(['kubectl', '-n', 'rotation-training', 'exec', 'deployment/probe',
    '--', 'python3', '-c', code, ca, expected], check=True)
```

Run `python3 verify-rotation.py`. Allow a short reconciliation delay and retry if the old leaf remains served. Compare `probe-old` and `probe-next` certificate fingerprints if you need to establish that the replacement differs. The CA and hostname checks stay enabled throughout.

## Common pitfalls

> [!WARNING]
> An existing TLS connection can continue using its original session. Test a fresh connection after rotation. `curl -k` and an unverified certificate dump can show a new certificate while hiding a broken trust chain or hostname.
