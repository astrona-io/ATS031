---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Secure Three Namespaces With Network Policies Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-capstone-010)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-capstone-010" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Inspect and explain

Start from the facts the policies need: the labels, the broken policy and the API server endpoint.

```sh
kubectl get pods --all-namespaces --show-labels
kubectl -n starfleet get networkpolicy probe-from-outpost -o yaml
kubectl get endpointslice -l kubernetes.io/service-name=kubernetes -o jsonpath='{.items[0].endpoints[0].addresses[0]}{"\n"}{.items[0].ports[0].port}{"\n"}'
```

The existing policy has two list entries, so it admits every pod of `outpost` and every `shuttle` pod. The repair puts both selectors into one entry. The last command prints the API server endpoint address and its port. Calico matches the endpoint address after the Service address translation, so the rule uses that address. In a `kind` cluster the port is normally 6443.

## Baselines

Save this as `networkpolicy-default-deny-all-starfleet.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: starfleet
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

Apply it:

```sh
kubectl apply -f networkpolicy-default-deny-all-starfleet.yaml
```

Save this as `networkpolicy-default-deny-all-outpost.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: outpost
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

Apply it:

```sh
kubectl apply -f networkpolicy-default-deny-all-outpost.yaml
```

Save this as `networkpolicy-default-deny-all-dock.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: dock
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

Apply it:

```sh
kubectl apply -f networkpolicy-default-deny-all-dock.yaml
```

## Repair the cross-namespace rule

Save this as `networkpolicy-probe-from-outpost.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: probe-from-outpost
  namespace: starfleet
spec:
  podSelector:
    matchLabels:
      app: probe
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: outpost
      podSelector:
        matchLabels:
          app: shuttle
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-probe-from-outpost.yaml
```

## Egress for the shuttle pod

Save this as `networkpolicy-shuttle-egress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: shuttle-egress
  namespace: outpost
spec:
  podSelector:
    matchLabels:
      app: shuttle
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: starfleet
      podSelector:
        matchLabels:
          app: probe
    ports:
    - protocol: TCP
      port: 8080
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
  - to:
    - ipBlock:
        cidr: 203.0.113.0/24
        except:
        - 203.0.113.99/32
    ports:
    - protocol: TCP
      port: 443
```

Apply it:

```sh
kubectl apply -f networkpolicy-shuttle-egress.yaml
```

## Egress for the scout pod

Replace `<API_ADDRESS>` and `<API_PORT>` with the two values printed by the EndpointSlice command above. Save this as `networkpolicy-scout-egress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: scout-egress
  namespace: dock
spec:
  podSelector:
    matchLabels:
      app: scout
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
  - to:
    - ipBlock:
        cidr: <API_ADDRESS>/32
    ports:
    - protocol: TCP
      port: <API_PORT>
```

Apply it:

```sh
kubectl apply -f networkpolicy-scout-egress.yaml
```

## Verify the result

The first request must return the `probe` response, and the script must print `dns=ok api=ok`. The other requests must time out. Run the checks one by one.

```sh
kubectl -n outpost exec shuttle -- wget -q -T 3 -O- http://probe.starfleet/
kubectl -n dock exec scout -- python /app/check.py
PROBE_IP=$(kubectl -n starfleet get pod -l app=probe -o jsonpath='{.items[0].status.podIP}')
TELEMETRY_IP=$(kubectl -n dock get pod telemetry -o jsonpath='{.status.podIP}')
kubectl -n outpost exec drifter -- wget -q -T 3 -O- "http://$PROBE_IP:8080/"
kubectl -n outpost exec shuttle -- wget -q -T 3 -O- "http://$TELEMETRY_IP:8080/"
```

A request from the `scout` pod to the `probe` pod address must also fail. Run it with Python inside the pod and read the message:

```sh
kubectl -n dock exec scout -- python -c "import urllib.request; urllib.request.urlopen('http://$PROBE_IP:8080/', timeout=3)"
```

After recording the result, remove this independent lab with `astrona destroy ats-031-capstone-010`.

## Common pitfalls

> [!WARNING]
> - **Applying the baseline before the allow rules and stopping.** A baseline alone breaks DNS and every path.
> - **Allowing the API Service address only.** Use the endpoint address and port from the EndpointSlice.
> - **Leaving two list entries in `probe-from-outpost`.** One entry combines the namespace and the pod.
> - **Opening ports wider than listed.** Every rule needs explicit ports.
