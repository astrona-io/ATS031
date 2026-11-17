---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow A TCP Port Range And A Named UDP Port Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-03-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-03-05" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

A port item can cover a range: `port` is the first port and `endPort` is the last one, both included. A port item can also name a container port by the name in the pod spec, such as `tick`, instead of the number. A rule with several port items allows any of them.

Save this as `networkpolicy-meter-ports.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: meter-ports
  namespace: starfleet-031-010-03-05
spec:
  podSelector:
    matchLabels:
      app: meter
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: outpost-031-010-03-05
      podSelector:
        matchLabels:
          app: surveyor
    ports:
    - protocol: TCP
      port: 7000
      endPort: 7002
    - protocol: UDP
      port: tick
```

Apply it:

```sh
kubectl apply -f networkpolicy-meter-ports.yaml
```

Then check the result. The test client prints `open` with the reply, `blocked` when no reply comes within three seconds, or `refused` when the port is open but nothing listens. Add `udp` instead of `tcp` for the UDP test:

```sh
METER_IP=$(kubectl -n starfleet-031-010-03-05 get pod meter -o jsonpath='{.status.podIP}')
kubectl -n outpost-031-010-03-05 exec surveyor -- python /app/client.py tcp "$METER_IP" 7002
kubectl -n outpost-031-010-03-05 exec surveyor -- python /app/client.py udp "$METER_IP" 7200
kubectl -n outpost-031-010-03-05 exec surveyor -- python /app/client.py tcp "$METER_IP" 7100
```

The first two commands must print `open`. The last one must print `blocked`.

The `surveyor` pod reaches TCP ports 7000 to 7002 and the UDP port named `tick`, and times out on TCP port 7100, which the rule does not list. The `loiterer` pod in the same namespace times out on every port, because the peer entry selects only `surveyor`.

When you are done, remove the lab with `astrona destroy ats-031-lab-010-03-05`.

## Common pitfalls

> [!WARNING]
> `endPort` needs a numeric `port`. A named port cannot start a range.
>
> A named port matches the name in the selected pod. If the pod has no port with that name, the rule allows nothing.
