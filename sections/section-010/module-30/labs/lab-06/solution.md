# Repair A Policy That Names The Service Port And Add A Port Range — Solution

You solve this lab by changing one NetworkPolicy. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Read the Service and both policies:

```sh
kubectl -n starfleet-031-010-03-06 get pods --show-labels
kubectl -n starfleet-031-010-03-06 get service kiosk -o yaml
kubectl -n starfleet-031-010-03-06 get networkpolicy default-deny-ingress -o yaml
kubectl -n starfleet-031-010-03-06 get networkpolicy kiosk-ingress -o yaml
```

The Service listens on port 80 and sends requests to `targetPort: http`, which is TCP port 8080 in the `kiosk` pods. The policy `default-deny-ingress` selects every pod in the namespace and allows no ingress. The policy `kiosk-ingress` allows the `visitor` pod on port 80.

## Step 2: allow the container port, not the Service port (check `service-port-repaired`)

kube-proxy translates the Service address to a pod address and the Service port to the container port. The network plugin checks the policy after that translation, so it sees TCP 8080, never port 80. A rule for port 80 matches nothing, and the default deny drops the request.

Write the `visitor` rule for port 8080.

## Step 3: add a rule for the metrics range (check `metrics-range`)

Ports and peers in one rule are combined: every peer of the rule may use every port of the rule. The `collector` pod needs other ports than the `visitor` pod, so it gets its own rule. One port item with `port: 9100` and `endPort: 9102` covers the three metrics ports.

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

## Step 4: test both senders (checks `service-port-repaired` and `collector-reaches-metrics`)

Every pod has a small test client. It prints `open` with the reply, or `blocked` when the connection times out. Test the Service and one pod address directly:

```sh
KIOSK_SERVICE_IP=$(kubectl -n starfleet-031-010-03-06 get service kiosk -o jsonpath='{.spec.clusterIP}')
KIOSK_POD_IP=$(kubectl -n starfleet-031-010-03-06 get pods -l app=kiosk -o jsonpath='{.items[0].status.podIP}')
kubectl -n starfleet-031-010-03-06 exec visitor -- python /app/client.py tcp "$KIOSK_SERVICE_IP" 80
kubectl -n starfleet-031-010-03-06 exec visitor -- python /app/client.py tcp "$KIOSK_POD_IP" 8080
kubectl -n starfleet-031-010-03-06 exec collector -- python /app/client.py tcp "$KIOSK_POD_IP" 9100
kubectl -n starfleet-031-010-03-06 exec collector -- python /app/client.py tcp "$KIOSK_POD_IP" 9102
```

All four commands must print `open`. Now test the paths that must stay closed:

```sh
kubectl -n starfleet-031-010-03-06 exec visitor -- python /app/client.py tcp "$KIOSK_POD_IP" 9101
kubectl -n starfleet-031-010-03-06 exec collector -- python /app/client.py tcp "$KIOSK_POD_IP" 8080
```

Both must print `blocked`, because each rule names its own sender and its own ports. Repeat the pod tests with `{.items[1].status.podIP}` for the second replica.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Write the container port, or its name `http`, in a policy. Port 80 is the Service port and never reaches the network plugin.
>
> Put each sender in its own rule. One rule with both `podSelector` entries and all ports lets `visitor` reach the metrics ports and `collector` reach 8080.
>
> Use one port item with `port: 9100` and `endPort: 9102`, and open no other port. Three separate items do not pass.
>
> Repair `kiosk-ingress` in place. Do not change or delete `default-deny-ingress`, and do not add a third policy.
