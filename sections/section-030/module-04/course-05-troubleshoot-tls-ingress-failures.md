# Troubleshoot TLS Ingress Failures

A client that cannot connect gives you one line: a certificate error, a reset or a 404 response. The cause can be in the Secret, the Ingress, the IngressClass or the controller, and the same line can come from several of them.

A fixed order of checks keeps you from guessing. On this page, you learn that order and apply it to four broken Ingresses, `case-one` to `case-four`, that the playground already holds.

## The order of checks

The checks start at the objects nearest to the Kubernetes API and end with the controller log. Each step rules out one cause:

1. Does the Ingress exist, and which class and host does it name? `kubectl -n starfleet get ingress` and `describe`.
2. Does the class belong to a controller that runs? `kubectl get ingressclass` shows `traefik` only.
3. Does the Secret exist in the same namespace, with the right type and keys? `kubectl -n starfleet get secret`.
4. Do the certificate and the key belong together, and does the SAN contain the host? Decode and compare.
5. What does the controller say? `kubectl -n ingress-system logs deployment/traefik`.

The SAN (Subject Alternative Name) is the list of host names a certificate is valid for. An IngressClass is the object that names the controller that serves an Ingress. Start with the first three checks, which only list objects:

<!-- astrona:playground:renew -->

```sh
kubectl get ingressclass
kubectl -n starfleet get ingress
kubectl -n starfleet get secret
```

You see the class `traefik`, five Ingresses and the Secrets `probe-tls`, `one-cert`, `two-tls`, `three-tls` and `four-tls`. There is no Secret `one-tls`, although `case-one` names it. That is the first clue.

## Read the controller log

The objects tell you what is configured. The log tells you what Traefik made of it. Traefik writes a line when it cannot use a Secret or a router. Filter the log for the cases:

```sh
kubectl -n ingress-system logs deployment/traefik --tail=200 | grep -iE 'case-|secret|tls|error' | tail -n 20
```

The lines name the Ingress and the problem, for example that a Secret was not found. The exact wording depends on the Traefik version, so match on the Ingress name and the word `error`.

## The four cases

With the order of checks and the log in hand, you can find the cause of each broken Ingress. The commands read the Secret name of `case-one`, compare the public keys of the certificate and the key in `two-tls`, and read the host of `case-three` and the class of `case-four`:

```sh
kubectl -n starfleet get ingress case-one -o jsonpath='{.spec.tls[0].secretName}{"\n"}'
kubectl -n starfleet get secret two-tls -o jsonpath='{.data.tls\.crt}' | base64 --decode | openssl x509 -noout -pubkey | openssl sha256
kubectl -n starfleet get secret two-tls -o jsonpath='{.data.tls\.key}' | base64 --decode | openssl pkey -pubout | openssl sha256
kubectl -n starfleet get ingress case-three -o jsonpath='{.spec.rules[0].host}{"\n"}'
kubectl -n starfleet get ingress case-four -o jsonpath='{.spec.ingressClassName}{"\n"}'
```

The results point to four different causes:

- **case-one:** the Ingress names `one-tls`, which does not exist. A working certificate exists as `one-cert`. Fix the Ingress to name `one-cert`, or create a Secret with the missing name.
- **case-two:** `two-tls` has the right type, but the key does not match the certificate. The two hashes differ. Create a new Secret from a matching pair.
- **case-three:** the host is `three.example.tset`, a typo. Clients ask for `three.example.test`, so their requests match no router. Fix the host in the rule and in the `tls` entry.
- **case-four:** the class is `nginx`, and no controller serves it. The API server accepts the Ingress, and every controller ignores it. Set `ingressClassName: traefik`.

![Diagram: the checks in order, IngressClass served, Secret exists in the same namespace, key matches certificate, host and SAN right, with the case that fails each one: case-four at the class check because it names nginx, case-one at the Secret check because one-tls does not exist, case-two at the key check because the key belongs to another pair, and case-three at the host check because of the typo tset](images/where-each-case-breaks.svg)

The drawing places each case at the check it fails. Each broken Ingress fails at a different step, which is why the same symptom on the client can have four causes.

To repair a case, apply a JSON patch and read the result back. Here is the repair for the class of `case-four`:

```sh
kubectl -n starfleet patch ingress case-four --type=json -p '[{"op":"replace","path":"/spec/ingressClassName","value":"traefik"}]'
kubectl -n starfleet get ingress case-four -o jsonpath='{.spec.ingressClassName}{"\n"}'
```

The order of checks also works as a decision tree. You ask one question at a time, and each "no" points to one repair.

![Diagram: a decision tree for a failing TLS request; is the class served, does the Secret exist in the same namespace, does the key match the certificate, are the host and the SAN right; each no leads to one fix, and four yes answers lead to the controller log](images/tls-troubleshooting-tree.svg)

The drawing turns the order of checks into a tree, from the object nearest to the API down to the controller log.

You can now trace a failing TLS Ingress in a fixed order, from the class to the Secret, the key pair, the host and the log, and repair it with a patch. Each check needs only `kubectl` and `openssl`. The question that stays open is how to notice these failures before a client reports them.

## Common pitfalls

> [!WARNING]
> - **Reading only the Ingress.** The API server accepts it even when its class, host or Secret is wrong. Check the Secret and the log too.
> - **Fixing the host in `rules` and not in `tls`.** Both lists name the host.
> - **Using `-k` to hide a certificate problem.** The problem is still there for real clients.
> - **Deleting the Ingress to start over.** You lose the evidence. Compare the object with a working one first.
