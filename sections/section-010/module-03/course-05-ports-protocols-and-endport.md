---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Ports, Protocols And endPort

A peer says who may connect. The `ports` list says to which port and over which protocol. A rule with a correct peer and a wrong port blocks the application, and a rule without a `ports` list opens every port. This part writes the port forms (single port, protocol, port range with `endPort`, named port) for the `telemetry` pod in `dock`, which listens on TCP and UDP.

## What the telemetry pod listens on

The `telemetry` pod has two listeners. A TCP listener on port 9000 carries the container port name `feed`, and a UDP listener on port 9001 carries the name `pulse`. Both answer each message with one line of text. Read the declared ports from the pod:

<!-- astrona:playground:renew -->

```sh
kubectl -n dock delete networkpolicy --all
kubectl -n dock get pod telemetry -o jsonpath='{.spec.containers[0].ports}'
TELEMETRY_IP=$(kubectl -n dock get pod telemetry -o jsonpath='{.status.podIP}')
```

The first command removes policies left in `dock`. The second prints the container ports with their names, numbers and protocols. The third stores the pod address for the tests.

## The port forms

Each item of `ports` has a `port`, an optional `protocol` and an optional `endPort`. The `protocol` is `TCP`, `UDP` or `SCTP` and defaults to `TCP`. A rule for TCP does not allow UDP on the same number, so a service that uses both needs two items. A `port` can be a number or the name of a container port. An `endPort` turns a number into an inclusive range from `port` to `endPort`, and the field is stable since Kubernetes 1.25. It works only with a numeric `port`, and the plugin must support it.

If a rule has no `ports` list, it applies to all ports and all protocols for its peers. An empty list and a missing list both mean "all ports", which is the reverse of what many readers expect.

## Write the policy

The policy allows `shuttle` in `starfleet` to reach `telemetry` on TCP ports 9000 to 9009 and on the UDP port named `pulse`. The peer is one entry with the namespace name and the pod label. Save this as `networkpolicy-telemetry-ports.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: telemetry-ports
  namespace: dock
spec:
  podSelector:
    matchLabels:
      app: telemetry
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: starfleet
      podSelector:
        matchLabels:
          app: shuttle
    ports:
    - protocol: TCP
      port: 9000
      endPort: 9009
    - protocol: UDP
      port: pulse
```

Apply it:

```sh
kubectl apply -f networkpolicy-telemetry-ports.yaml
```

Then check the result. Each command runs from the `shuttle` pod in `starfleet`. The TCP request to port 9000 must print the text line of the listener. The UDP message goes to port 9001, and the listener must answer it. The TCP request to port 9100 is outside the range and must end after the limit without any answer.

```sh
kubectl -n starfleet exec shuttle -- nc -w 3 "$TELEMETRY_IP" 9000
kubectl -n starfleet exec shuttle -- sh -c "echo ping | nc -u -w 3 $TELEMETRY_IP 9001"
kubectl -n starfleet exec shuttle -- nc -w 3 "$TELEMETRY_IP" 9100
```

Port 9100 has no listener in the pod. Without a policy it would produce an immediate refusal. With the policy it ends by timeout, because the plugin drops the packet before it reaches the pod. This is the same timeout versus refusal signal as before, now applied to a port. UDP tests are weaker than TCP tests: a missing answer can also mean a dropped reply, so rely on the TCP result when both are available.

## Named ports

A named port ties the rule to the name in the pod specification, not to a number. If a Deployment changes the number behind `pulse`, the policy keeps working. The name is resolved per destination pod, so pods that use the same name on different numbers are each matched on their own number. A name that no selected pod declares matches nothing, and the connection stays blocked.

## Several items in one list

Every item in `ports` is an alternative, like every item in `from`. The rule above has two items and allows the union of them. If you need different ports for different peers, write two rules, each with its own `from` and `ports`. Peers and ports in one rule combine as "any peer on any port of this rule".

```sh
kubectl -n dock delete networkpolicy telemetry-ports
```

You can now write every port form and test it with a request. The last part looks at how policies meet Services and changing pods.

## Common pitfalls

> [!WARNING]
> - **Omitting `ports`.** The rule then allows every port for its peers.
> - **Assuming TCP covers UDP.** Protocols are separate; add an item for each.
> - **Using `endPort` with a named port.** A range needs numbers.
> - **Using the Service port.** Policies see the pod port after the Service forwards the request.
