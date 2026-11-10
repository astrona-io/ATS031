---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Repair A TLS Ingress With A Missing Secret Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-03-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-03-02" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Find the cause

```sh
kubectl -n starfleet-031-030-03-02 get ingress beacon -o jsonpath='{.spec.tls[0].secretName}{"\n"}'
kubectl -n starfleet-031-030-03-02 get secret
kubectl get secret --all-namespaces | grep beacon-tls
kubectl -n outpost-031-030-03-02 get secret beacon-tls -o jsonpath='{.data.tls\.crt}' | base64 --decode | openssl x509 -noout -subject -ext subjectAltName
```

The Ingress names `beacon-tls`, the Secret does not exist in `starfleet-031-030-03-02` and the copy in `outpost-031-030-03-02` has no SAN extension. An Ingress cannot use a Secret from another namespace, and a certificate without a SAN is not accepted by current clients.

## Create the correct Secret

```sh
openssl req -x509 -nodes -newkey rsa:2048 -days 30 -keyout beacon.key -out beacon.crt -subj "/CN=beacon.example.test" -addext "subjectAltName=DNS:beacon.example.test"
kubectl -n starfleet-031-030-03-02 create secret tls beacon-tls --cert=beacon.crt --key=beacon.key
```

## Verify

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443
curl -s --cacert beacon.crt --resolve beacon.example.test:8443:127.0.0.1 https://beacon.example.test:8443/
```

The command prints the `beacon` response. The Ingress itself needs no change, because it already names `beacon-tls` in its own namespace.
## Common pitfalls

> [!WARNING]
> - **Copying the Secret from `outpost-031-030-03-02`.** Its certificate has no SAN.
> - **Editing the Ingress to a new Secret name.** The required result keeps `beacon-tls`.
> - **Waiting without checking.** If the response is still wrong, read the Traefik log.

## Clean up

Destroy the lab cluster when you are done:

```sh
astrona destroy ats-031-lab-030-03-02
```
