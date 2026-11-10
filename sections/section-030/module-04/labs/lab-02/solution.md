---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Repair Four Broken TLS Ingresses Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-030-04-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-030-04-02" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Find the cause for each Ingress

```sh
kubectl -n starfleet-031-030-04-02 get ingress
kubectl -n starfleet-031-030-04-02 get secret
for name in alpha bravo charlie delta; do
  echo "== $name"
  kubectl -n starfleet-031-030-04-02 get ingress $name -o jsonpath='class={.spec.ingressClassName} host={.spec.rules[0].host} tls-hosts={.spec.tls[0].hosts} secret={.spec.tls[0].secretName}{"\n"}'
done
kubectl -n starfleet-031-030-04-02 get secret bravo-tls -o jsonpath='{.data.tls\.crt}' | base64 --decode | openssl x509 -noout -pubkey | openssl sha256
kubectl -n starfleet-031-030-04-02 get secret bravo-tls -o jsonpath='{.data.tls\.key}' | base64 --decode | openssl pkey -pubout | openssl sha256
```

The four causes are these:

- `alpha` names `alpha-tls`, which does not exist. The working Secret is `alpha-cert`.
- `bravo` has the Secret `bravo-tls`, but the key does not match the certificate. The two hashes differ.
- `charlie` has a host that is misspelled in the rule.
- `delta` has class `nginx`, which no controller serves.

## Repair them

```sh
kubectl -n starfleet-031-030-04-02 patch ingress alpha --type=json -p '[{"op":"replace","path":"/spec/tls/0/secretName","value":"alpha-cert"}]'
kubectl -n starfleet-031-030-04-02 delete secret bravo-tls
openssl req -x509 -nodes -newkey rsa:2048 -days 30 -keyout bravo.key -out bravo.crt -subj "/CN=bravo.example.test" -addext "subjectAltName=DNS:bravo.example.test"
kubectl -n starfleet-031-030-04-02 create secret tls bravo-tls --cert=bravo.crt --key=bravo.key
kubectl -n starfleet-031-030-04-02 patch ingress charlie --type=json -p '[{"op":"replace","path":"/spec/rules/0/host","value":"charlie.example.test"}]'
kubectl -n starfleet-031-030-04-02 patch ingress delta --type=json -p '[{"op":"replace","path":"/spec/ingressClassName","value":"traefik"}]'
```

## Verify

Open a port forward in a second terminal. The Secrets for `alpha` and `bravo` hold the certificates, so extract and test one of them:

```sh
kubectl -n ingress-system port-forward service/traefik 8443:443
kubectl -n starfleet-031-030-04-02 get secret alpha-cert -o jsonpath='{.data.tls\.crt}' | base64 --decode > alpha.crt
curl -s --cacert alpha.crt --resolve alpha.example.test:8443:127.0.0.1 https://alpha.example.test:8443/
```

Repeat for the other hosts with the certificate of their own Secret.
## Common pitfalls

> [!WARNING]
> - **Fixing only what the first error shows.** Each Ingress has its own cause; check all four.
> - **Editing the host in `rules` but not in `tls`.** Both lists must name the host. Check which list is wrong first.
> - **Deleting Ingresses.** The task forbids it and you lose the evidence.

## Clean up

Destroy the lab cluster when you are done:

```sh
astrona destroy ats-031-lab-030-04-02
```
