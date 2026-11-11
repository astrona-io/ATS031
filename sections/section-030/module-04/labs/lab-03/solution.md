---
draft: true
---
# Solution

Replace the active pair:

```sh
kubectl -n rotation-training get secret probe-next -o json | python3 -c 'import json,sys; s=json.load(sys.stdin); print(json.dumps({"apiVersion":"v1","kind":"Secret","metadata":{"name":"probe-tls","namespace":"rotation-training"},"type":"kubernetes.io/tls","data":s["data"]}))' | kubectl apply -f -
```

Run the preparation lesson's verified connection test. Check the replacement leaf and HTTP response after the controller reloads the Secret.
