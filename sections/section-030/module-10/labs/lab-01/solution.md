# Terminate TLS At The Ingress And Verify The Server Name — Solution

You solve this lab with one Ingress. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the application, the Secret and the Ingress class, and that no Ingress exists yet:

```sh
kubectl -n starfleet-031-030-01-01 get deployment,service probe
kubectl -n starfleet-031-030-01-01 get secret probe-tls
kubectl get ingressclass traefik
kubectl -n starfleet-031-030-01-01 get ingress
```

The Service `probe` listens on port 80 and sends traffic to the pods on port 8080. The Secret `probe-tls` has the type `kubernetes.io/tls`: it holds a certificate (`tls.crt`) and its private key (`tls.key`). The certificate names `probe.local` in its Subject Alternative Name (SAN), the list of host names the certificate is valid for.

## Step 2: route probe.local to the Service (check `probe-ingress`)

An Ingress is a Kubernetes object that tells an Ingress controller how to route HTTP requests to Services. `spec.ingressClassName: traefik` hands this Ingress to the Traefik controller. The rule matches requests for the host `probe.local` and every path under `/`, and sends them to Service `probe` on port 80.

## Step 3: add TLS on the websecure entrypoint (check `probe-tls`)

Transport Layer Security (TLS) encrypts the connection and proves the server's name with a certificate. Traefik listens for HTTPS on its entrypoint `websecure` (port 443 of the Service `traefik`). The annotation `traefik.ingress.kubernetes.io/router.entrypoints: websecure` binds the route to that entrypoint, and `spec.tls` names the Secret Traefik uses for `probe.local`. Traefik terminates TLS: it decrypts the request and forwards plain HTTP to the pods.

Save this as `ingress-probe.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: probe
  namespace: starfleet-031-030-01-01
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    traefik.ingress.kubernetes.io/router.tls: 'true'
spec:
  ingressClassName: traefik
  rules:
  - host: probe.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: probe
            port:
              number: 80
  tls:
  - hosts:
    - probe.local
    secretName: probe-tls
```

Apply it:

```sh
kubectl apply -f ingress-probe.yaml
```

The host in `spec.tls` must match the host in the rule. Traefik serves the `probe-tls` certificate only when the client asks for the server name `probe.local` in the TLS handshake (Server Name Indication, SNI).

## Step 4: test the matching and the wrong name (check `probe-https`)

Save the certificate from the Secret, so `curl` can trust it, and forward the Traefik HTTPS port to your machine:

```sh
kubectl -n starfleet-031-030-01-01 get secret probe-tls -o jsonpath='{.data.tls\.crt}' | base64 -d > probe.crt
kubectl -n ingress-system port-forward service/traefik 8443:443 >/dev/null &
```

Wait a second for the port forward, then send one request for the right name and one for a wrong name. `--resolve` sends both to the forwarded port:

```sh
curl --cacert probe.crt --resolve probe.local:8443:127.0.0.1 https://probe.local:8443/
curl --cacert probe.crt --resolve wrong.local:8443:127.0.0.1 https://wrong.local:8443/
```

The first command must print a line that starts with `version=v1`. The second must fail with a certificate error and print no reply: Traefik has no certificate for `wrong.local`, and `probe.crt` is not valid for that name. Stop the port forward with `kill %1`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Without the annotation `traefik.ingress.kubernetes.io/router.entrypoints: websecure`, the Ingress does not match the required fields, even when `spec.tls` is set.
>
> If the host under `spec.tls` or the `secretName` is wrong, Traefik serves its own default certificate for `probe.local`, and a client that trusts only `probe-tls` rejects the connection.
>
> Do not turn off certificate checks (`curl -k`) to make the test pass. The check verifies the certificate and the server name, so a test without verification proves nothing.
>
> Do not edit the Deployment `probe`. The check expects its two replicas, the label `release: probe` and `VERSION=v1` unchanged.
