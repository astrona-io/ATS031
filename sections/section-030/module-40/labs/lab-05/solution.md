---
exam_objectives:
- Properly set up Ingress with TLS
---
# Rotate An Expiring Certificate Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-04-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-04-05" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Find the expiring certificate

`-checkend` answers whether the certificate is still valid after the given number of seconds. 604,800 seconds are seven days:

```sh
kubectl -n starfleet-031-030-04-05 get secret orbit-tls -o jsonpath='{.data.tls\.crt}' | base64 -d > orbit-old.crt
openssl x509 -in orbit-old.crt -noout -enddate -serial
openssl x509 -in orbit-old.crt -noout -checkend 604800
```

The last command prints `Certificate will expire`.

## Create the new key and certificate

```sh
openssl req -x509 -newkey rsa:2048 -nodes -days 90 -keyout orbit.key -out orbit.crt -subj "/CN=orbit.example.test" -addext "subjectAltName=DNS:orbit.example.test"
```

## Replace the Secret in place

`kubectl create secret` refuses to overwrite an existing Secret. Write the new Secret to a file first, then apply it over the old one. The name stays the same, so the Ingress needs no change:

```sh
kubectl -n starfleet-031-030-04-05 create secret tls orbit-tls --cert=orbit.crt --key=orbit.key --dry-run=client -o yaml > secret-orbit-tls.yaml
kubectl apply -f secret-orbit-tls.yaml
```

## Verify the served certificate

Traefik watches the Secret and loads the new certificate without a restart. Open a port forward in a second terminal and compare the serial numbers:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443
openssl s_client -connect 127.0.0.1:8443 -servername orbit.example.test </dev/null 2>/dev/null | openssl x509 -noout -serial -enddate
openssl x509 -in orbit.crt -noout -serial
```

The served serial number equals the serial of `orbit.crt`, and the end date is 90 days away.

## Common pitfalls

> [!WARNING]
> - **Deleting the Secret before you create the new one.** Traefik serves its default certificate during the gap. Apply the new data over the old Secret.
> - **Reusing the old key.** A rotation after a suspected leak must use a new key; create a new one each time.
> - **Creating a Secret with a new name.** Then the Ingress still points to the old Secret, and you must change the Ingress too.

## Clean up

Destroy the lab cluster when you are done:

```sh
astrona destroy ats-031-lab-030-04-05
```
