---
exam_objectives:
- Properly set up Ingress with TLS
---
# Require Client Certificates On One Route Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-04-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-04-03" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Give Traefik the client CA

Extract the CA certificate from the Secret and store it in the ConfigMap that the Traefik pod mounts:

```sh
kubectl -n starfleet-031-030-04-03 get secret crew-client -o jsonpath='{.data.ca\.crt}' | base64 -d > client-ca.crt
kubectl -n starfleet-031-030-04-03 get secret crew-client -o jsonpath='{.data.tls\.crt}' | base64 -d > crew.crt
kubectl -n starfleet-031-030-04-03 get secret crew-client -o jsonpath='{.data.tls\.key}' | base64 -d > crew.key
openssl verify -CAfile client-ca.crt crew.crt
kubectl -n ingress-system create configmap client-ca --from-file=client-ca.crt
```

`openssl verify` prints `crew.crt: OK`, so the client certificate belongs to this CA.

## Add the TLS option

Save this as `dynamic.yaml`:

```yaml
tls:
  options:
    default:
      minVersion: VersionTLS12
    mtls:
      minVersion: VersionTLS12
      clientAuth:
        clientAuthType: RequireAndVerifyClientCert
        caFiles:
        - /etc/traefik/client-ca/client-ca.crt
```

Apply it by replacing the ConfigMap from the file, then restart Traefik so the pod mounts the new `client-ca` ConfigMap:

```sh
kubectl -n ingress-system create configmap traefik-dynamic --from-file=dynamic.yaml --dry-run=client -o yaml > configmap-traefik-dynamic.yaml
kubectl apply -f configmap-traefik-dynamic.yaml
kubectl -n ingress-system rollout restart deployment/traefik
kubectl -n ingress-system rollout status deployment/traefik
```

## Attach the option to vault only

Save this as `ingress-vault.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vault
  namespace: starfleet-031-030-04-03
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    traefik.ingress.kubernetes.io/router.tls: 'true'
    traefik.ingress.kubernetes.io/router.tls.options: mtls@file
spec:
  ingressClassName: traefik
  rules:
  - host: vault.example.test
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: vault
            port:
              number: 80
  tls:
  - hosts:
    - vault.example.test
    secretName: vault-tls
```

Apply it:

```sh
kubectl apply -f ingress-vault.yaml
```

## Verify

Open a port forward in a second terminal, then call `vault` without and with the client certificate:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443
kubectl -n starfleet-031-030-04-03 get secret vault-tls -o jsonpath='{.data.tls\.crt}' | base64 -d > vault.crt
curl -s --cacert vault.crt --resolve vault.example.test:8443:127.0.0.1 https://vault.example.test:8443/ ; echo "exit=$?"
curl -s --cacert vault.crt --cert crew.crt --key crew.key --resolve vault.example.test:8443:127.0.0.1 https://vault.example.test:8443/
```

The first command fails with a non-zero exit code. The second returns a line that starts with `app=vault`.

## Common pitfalls

> [!WARNING]
> - **Putting the option on the default TLS option.** Then every route, including `beacon`, requires client certificates.
> - **Creating the `client-ca` ConfigMap without restarting Traefik.** The pod may not see a ConfigMap that did not exist when it started.
> - **Using `RequestClientCert`.** It asks for a certificate but lets clients without one through.

## Clean up

Destroy the lab cluster when you are done:

```sh
astrona destroy ats-031-lab-030-04-03
```
