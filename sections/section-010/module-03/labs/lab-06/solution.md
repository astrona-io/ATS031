---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Repair A Policy That Names The Service Port And Add A Port Range Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-03-06)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-03-06" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

The policy `kiosk-ingress` allows port 80, the Service port. The network plugin checks traffic after kube-proxy has translated the Service address to a pod address and the Service port to the container port. The `kiosk` pods listen on port 8080 (named `http`), so a rule for port 80 matches nothing.

Look at the Service and the policy:

```sh
kubectl -n starfleet-031-010-03-06 get service kiosk -o yaml
kubectl -n starfleet-031-010-03-06 get networkpolicy kiosk-ingress -o yaml
```

The Service sends port 80 to `targetPort: http`, which is port 8080 in the pods. Write the rule for port 8080 and add a second rule for the metrics ports.

Save this as `networkpolicy-kiosk-ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: kiosk-ingress
  namespace: starfleet-031-010-03-06
spec:
  podSelector:
    matchLabels:
      app: kiosk
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: visitor
    ports:
    - protocol: TCP
      port: 8080
  - from:
    - podSelector:
        matchLabels:
          app: collector
    ports:
    - protocol: TCP
      port: 9100
      endPort: 9102
```

Apply it:

```sh
kubectl apply -f networkpolicy-kiosk-ingress.yaml
```

Then check the result. The test client prints `open` with the reply, or `blocked` when the connection times out. Test the Service and one pod address directly:

```sh
KIOSK_SERVICE_IP=$(kubectl -n starfleet-031-010-03-06 get service kiosk -o jsonpath='{.spec.clusterIP}')
KIOSK_POD_IP=$(kubectl -n starfleet-031-010-03-06 get pods -l app=kiosk -o jsonpath='{.items[0].status.podIP}')
kubectl -n starfleet-031-010-03-06 exec visitor -- python /app/client.py tcp "$KIOSK_SERVICE_IP" 80
kubectl -n starfleet-031-010-03-06 exec collector -- python /app/client.py tcp "$KIOSK_POD_IP" 9101
kubectl -n starfleet-031-010-03-06 exec visitor -- python /app/client.py tcp "$KIOSK_POD_IP" 9101
```

The first two commands must print `open` and the last one must print `blocked`. Repeat the pod test with `{.items[1].status.podIP}` for the second replica.

The `visitor` pod reaches the Service again, because the rule now allows the container port. The `collector` pod reaches ports 9100 to 9102 but not port 8080, and the `visitor` pod cannot reach the metrics ports, because each rule names its own sender and its own ports.

When you are done, remove the lab with `astrona destroy ats-031-lab-010-03-06`.

## Common pitfalls

> [!WARNING]
> Write the container port, or its name, in a policy. The Service port never reaches the network plugin.
>
> Ports and peers in one rule are combined: put each sender in its own rule when the senders need different ports.
