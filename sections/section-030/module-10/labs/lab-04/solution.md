# Give Each Ingress Host Its Own TLS Certificate — Solution

You solve this lab by changing the `tls` section of one Ingress. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Read the `tls` section and the Subject Alternative Name (SAN) of the `dock-tls` certificate. The SAN is the list of host names a certificate is valid for:

```sh
kubectl -n starfleet-031-030-01-04 get ingress fleet -o jsonpath='{range .spec.tls[*]}{.hosts} {.secretName}{"\n"}{end}'
kubectl -n starfleet-031-030-01-04 get secret dock-tls -o jsonpath='{.data.tls\.crt}' | base64 --decode > dock.crt
openssl x509 -in dock.crt -noout -ext subjectAltName
```

The single `tls` entry lists both hosts with `bridge-tls`, so Traefik never loads the certificate in `dock-tls`. The `dock-tls` certificate names `DNS:dock.local`.

## Step 2: give bridge.local its own entry (check `bridge-entry`)

Traefik picks a certificate by the server name that the client sends in the TLS handshake, which is called Server Name Indication (SNI). Each `spec.tls` entry tells Traefik to load one Secret for the hosts it lists. The `bridge-tls` certificate names only `bridge.local`, so its entry must list only `bridge.local`.

## Step 3: give dock.local its own entry (check `fleet-tls`)

Add a second entry that loads `dock-tls` for `dock.local`. Now Traefik has a certificate whose SAN matches each server name. Keep the annotations and both rules exactly as they are.

Save this as `ingress-fleet.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fleet
  namespace: starfleet-031-030-01-04
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    traefik.ingress.kubernetes.io/router.tls: 'true'
spec:
  ingressClassName: traefik
  rules:
  - host: bridge.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: bridge
            port:
              number: 80
  - host: dock.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: dock
            port:
              number: 80
  tls:
  - hosts:
    - bridge.local
    secretName: bridge-tls
  - hosts:
    - dock.local
    secretName: dock-tls
```

Apply it:

```sh
kubectl apply -f ingress-fleet.yaml
```

## Step 4: test both server names (check `dock-https`)

Save the `bridge-tls` certificate too, and forward the Traefik HTTPS port to your machine:

```sh
kubectl -n starfleet-031-030-01-04 get secret bridge-tls -o jsonpath='{.data.tls\.crt}' | base64 --decode > bridge.crt
kubectl -n ingress-system port-forward service/traefik 8443:443 >/dev/null &
```

Wait a second for the port forward, then connect to each host with only its own certificate as the trusted certificate:

```sh
curl -s --cacert dock.crt --resolve dock.local:8443:127.0.0.1 https://dock.local:8443/
curl -s --cacert bridge.crt --resolve bridge.local:8443:127.0.0.1 https://bridge.local:8443/
```

The first response starts with `app=dock` and the second with `app=bridge`. Stop the port forward with `kill %1`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not list several hosts with one Secret. The certificate in that Secret must name every host in its SAN, otherwise Traefik sends its default certificate and clients reject it.
>
> Do not edit the rules. The routes were correct, and the check expects both rules unchanged.
>
> Do not delete and create the Secrets again, and do not edit them. The check compares their UID and resource version with the starting state.
>
> Test with the server name. A request to `127.0.0.1` without SNI gets the default certificate.
