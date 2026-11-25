---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Playground Guide: Allow One Peer And Deny Another

Work in a shell on your own computer. `kubectl`, the Kubernetes command-line tool, normally already points at the playground cluster after the playground starts. A kubeconfig is the file that tells `kubectl` which cluster to use and which credentials to send. To be sure that you work on the playground and not on another cluster, select the playground's kubeconfig and check the context:

<!-- astrona:playground:renew -->

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-playground-010-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-playground-010-01" || exit 1
```

The `test` line stops the shell when the context belongs to another cluster. Keep this shell open while you work through the pages of the module.

## Look at the starting state

This playground is a `kind` cluster with the Calico network plugin, which enforces NetworkPolicy. The `starfleet` namespace runs the `probe` pods behind the `probe` Service and a `shuttle` client pod. The `outpost` namespace runs the `drifter` client pod. List the pods with their labels and the policies in `starfleet`:

```sh
kubectl -n starfleet get pods --show-labels
kubectl -n outpost get pods --show-labels
kubectl -n starfleet get networkpolicy -o yaml
```

A NetworkPolicy selects the destination pods and lists the traffic they may receive. A `podSelector` in a `from` rule without a `namespaceSelector` matches pods in the namespace of the policy only. Calico, the network plugin, enforces the rule; the API server only stores it.

## Allow one client

The policy below selects the `probe` pods and allows ingress only from pods labelled `app: shuttle` in `starfleet`, on TCP port 8080. Save this as `networkpolicy-probe-shuttle.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: probe-shuttle
  namespace: starfleet
spec:
  podSelector:
    matchLabels:
      app: probe
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: shuttle
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-probe-shuttle.yaml
```

## Check the result

Then check the result. Send a request from each client. The first command runs from `shuttle` in `starfleet` and must print the reply of `probe`. The second runs from `drifter` in `outpost` and must end with a timeout, because the policy does not allow it. A timeout means that Calico dropped the packets; an error such as a missing pod or a refused connection does not prove that the policy works.

```sh
kubectl -n starfleet exec shuttle -- wget -q -T 3 -O- http://probe/
kubectl -n outpost exec drifter -- wget -q -T 3 -O- http://probe.starfleet/
```

Run the two commands one by one. The second command returns a nonzero exit status when the denial works, so a shell script that stops on the first error would stop there.

## Common pitfalls

> [!WARNING]
> Policies combine their allowed traffic. Check a denied peer as well as an allowed peer. A missing client or refused listener is not evidence that the network policy enforced a timeout.
