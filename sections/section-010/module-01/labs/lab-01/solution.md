---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow One Peer And Deny Another Solution

Use a host shell with this lab's private kubeconfig. A kubeconfig is the file that tells kubectl, the Kubernetes command-line tool, which cluster to use and with which credentials. This lab runs in its own cluster, separate from the playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-01-01" || exit 1
```

Keep this connection for the whole task. Every script of the lab refuses to run against another context.

A NetworkPolicy is a Kubernetes object that limits which network traffic may reach or leave the pods it selects. The network plugin (here Calico) reads the policy and enforces it. In this lab one ingress policy on the `hub` pods admits the `tender` pod, and every other sender loses access because the `hub` pods become isolated for ingress.

The policy selects the `hub` pods with `podSelector`, lists only `Ingress` in `policyTypes`, and names the allowed sender with a second `podSelector` inside `from`. A `from` entry with only a `podSelector` means "pods with this label in the same namespace as the policy".

Save this as `networkpolicy-hub-from-tender.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: hub-from-tender
  namespace: starfleet-031-010-01-01
spec:
  podSelector:
    matchLabels:
      app: hub
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: tender
    ports:
    - protocol: TCP
      port: 8080
```

Apply it:

```sh
kubectl apply -f networkpolicy-hub-from-tender.yaml
```

Then check the result. The test client prints `open` with the reply, or `blocked` when the connection times out:

```sh
HUB_SERVICE_IP=$(kubectl -n starfleet-031-010-01-01 get service hub -o jsonpath='{.spec.clusterIP}')
kubectl -n starfleet-031-010-01-01 exec tender -- python /app/client.py tcp "$HUB_SERVICE_IP" 80
kubectl -n starfleet-031-010-01-01 exec idler -- python /app/client.py tcp "$HUB_SERVICE_IP" 80
kubectl -n outpost-031-010-01-01 exec stranger -- python /app/client.py tcp "$HUB_SERVICE_IP" 80
```

The first command must print `open`. The other two must print `blocked`.

The `tender` pod gets a reply because its label matches the `from` rule. The `idler` pod in the same namespace and the `stranger` pod in `outpost-031-010-01-01` time out, because no rule admits them. Both pods still reach the `mirror` pod: the policy only isolates the `hub` pods, so the block comes from the hub policy and not from a broken client.

When you are done, remove the lab with `astrona destroy ats-031-lab-010-01-01`.

## Common pitfalls

> [!WARNING]
> A policy changes nothing for pods it does not select. Test a denied sender and also prove that the same sender still reaches another pod, so you know the policy causes the block.
>
> Do not add a policy in the other namespace to block the `stranger` pod. The task asks for one policy on the `hub` pods; extra egress policies hide whether the ingress rule works.
