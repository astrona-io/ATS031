---
draft: true
---
# Verify CIDR Exceptions And Port Ranges

An `ipBlock` matches an address range, while `except` removes smaller ranges from it. A numeric `port` with `endPort` allows an inclusive range. Neither field has an effect unless the network plugin implements NetworkPolicy. This independent lab installs Calico and gives the server five working listeners so a blocked port can be distinguished from a stopped service.

<!-- astrona:playground:renew -->

Read the two client addresses and the server address:

```sh
kubectl -n ranges-training get pods -o wide
```

Save `bounded-range.yaml`, replacing `<EXCLUDED_IP>` with the excluded client's current address:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: bounded-range
  namespace: ranges-training
spec:
  podSelector:
    matchLabels:
      app: range-server
  policyTypes: [Ingress]
  ingress:
  - from:
    - ipBlock:
        cidr: 0.0.0.0/0
        except: [<EXCLUDED_IP>/32]
    ports:
    - protocol: TCP
      port: 8080
      endPort: 8082
```

Apply it and allow a few seconds for policy reconciliation:

```sh
kubectl apply -f bounded-range.yaml
```

Use the server's Pod IP for a fresh connection, replacing `<SERVER_IP>`:

```sh
kubectl -n ranges-training exec allowed -- python3 -c 'import socket; s=socket.create_connection(("<SERVER_IP>",8081),timeout=2); print(s.recv(80).decode())'
```

Repeat from `excluded` and test ports 8079, 8080, 8082 and 8083. The allowed client should receive `range-service` on 8080, 8081 and 8082. Requests to adjacent ports should time out. Confirm those listeners still answer from inside `server` against `127.0.0.1`; otherwise a stopped application could look like a working policy.

NetworkPolicy rules are additive. A second policy allowing every port defeats the range restriction even when `bounded-range` is correct. Inspect all policies when observed access is broader than expected.

## Common pitfalls

> [!WARNING]
> Pod addresses can change. The address-based exercise demonstrates matching, not a durable identity strategy. Use Pod and namespace selectors for application identities, and reserve `ipBlock` for address boundaries whose observed source or destination you have verified.
