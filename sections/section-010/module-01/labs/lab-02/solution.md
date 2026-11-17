---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow DNS And One Application Dependency Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-01-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-01-02" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Inspect And Explain

The application and client fixtures are healthy. Complete the required change without replacing unrelated resources.

Inspect the relevant evidence:

```sh
kubectl -n starfleet-031-010-01-02 get pods
kubectl -n starfleet-031-010-01-02 get deployment probe -o yaml
```

DNS lookup and application traffic are separate dependencies. Both need an allowance when the client is isolated for egress. Namespace and Pod selectors in the same peer item combine their requirements. Test a healthy denied listener as well as the intended Service so an overly broad policy cannot pass.


Save this as `pod-blocked-server.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: blocked-server
  namespace: starfleet-031-010-01-02
  labels:
    app: blocked-server
spec:
  restartPolicy: Never
  containers:
  - name: web
    image: docker.io/library/python:3.13-alpine
    command:
    - python
    - -m
    - http.server
    - '8080'
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: shuttle-egress
  namespace: starfleet-031-010-01-02
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
    - podSelector:
        matchLabels:
          app: probe
    ports:
    - protocol: TCP
      port: 8080
```

Apply the required change:

```sh
kubectl apply -f pod-blocked-server.yaml
```

## Verify The Result

Observe the actual result. A denied-request command returns a nonzero status when the denial works. Run denial checks separately from a shell sequence that stops on the first nonzero status.

```sh
kubectl -n starfleet-031-010-01-02 wait --for=condition=Ready pod/blocked-server --timeout=180s
kubectl -n starfleet-031-010-01-02 exec shuttle -- nslookup probe.starfleet-031-010-01-02.svc.cluster.local
kubectl -n starfleet-031-010-01-02 exec shuttle -- wget -q -T 3 -O- http://probe/
```

Create `shuttle-egress` selecting `app: shuttle`. Allow DNS on TCP and UDP port 53 only to kube-system Pods labelled `k8s-app: kube-dns`, and allow TCP 8080 only to same-namespace Pods labelled `app: probe`. Create a healthy `blocked-server` Pod with a different label. Shuttle must resolve and reach probe, while a direct request to the running blocked server must time out.

After recording the result, remove this independent lab with `astrona destroy ats-031-lab-010-01-02`.

## Common pitfalls

> [!WARNING]
> DNS and application connections require separate rules. Combine the DNS namespace and Pod selectors within one peer item. Verify that the unrelated listener is healthy before testing its denial.
