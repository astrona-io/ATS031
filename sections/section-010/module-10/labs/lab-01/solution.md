# Allow One Peer And Deny Another — Solution

You solve this lab with one NetworkPolicy. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Check the labels the policy will use, and that no policy exists yet:

```sh
kubectl -n starfleet-031-010-01-01 get pods --show-labels
kubectl -n outpost-031-010-01-01 get pods --show-labels
kubectl get networkpolicy -A
```

The `hub` pods carry `app: hub` and the sender you must allow carries `app: tender`. Without any policy, every pod can reach every other pod.

## Step 2: select the hub pods for ingress (check `hub-policy`)

A NetworkPolicy picks the pods it protects with `spec.podSelector`. Listing only `Ingress` in `policyTypes` means the policy controls traffic coming in to the `hub` pods and leaves their outgoing traffic alone.

Once a pod is selected by an ingress policy, it accepts only the traffic that some rule allows. That is what blocks every other sender.

## Step 3: allow only tender on TCP 8080 (checks `hub-policy` and `tender-allowed`)

Add one ingress rule. A `from` entry with only a `podSelector` matches pods with that label in the policy's own namespace. The `ports` list limits the rule to TCP 8080, the container port behind the Service `hub`.

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

Use port 8080, not 80. The Service listens on port 80, but the policy sees traffic after the Service has sent it on to the pod, so it must name the pod's port.

## Step 4: test allowed and blocked senders (checks `tender-allowed` and `others-denied`)

Every pod has a small test client. It prints `open` with the reply, or `blocked` when the connection times out:

```sh
HUB_SERVICE_IP=$(kubectl -n starfleet-031-010-01-01 get service hub -o jsonpath='{.spec.clusterIP}')
kubectl -n starfleet-031-010-01-01 exec tender -- python /app/client.py tcp "$HUB_SERVICE_IP" 80
kubectl -n starfleet-031-010-01-01 exec idler -- python /app/client.py tcp "$HUB_SERVICE_IP" 80
kubectl -n outpost-031-010-01-01 exec stranger -- python /app/client.py tcp "$HUB_SERVICE_IP" 80
```

The first command must print `open`. The other two must print `blocked`.

Now prove the block comes from the hub policy, not from a broken pod. `idler` and `stranger` must still reach `mirror`, which no policy selects:

```sh
MIRROR_IP=$(kubectl -n starfleet-031-010-01-01 get pod mirror -o jsonpath='{.status.podIP}')
kubectl -n starfleet-031-010-01-01 exec idler -- python /app/client.py tcp "$MIRROR_IP" 8080
kubectl -n outpost-031-010-01-01 exec stranger -- python /app/client.py tcp "$MIRROR_IP" 8080
```

Both must print `open`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not add a second policy, such as a default deny in `starfleet-031-010-01-01` or an egress policy in `outpost-031-010-01-01`. The task allows only `hub-from-tender`, and an extra policy would also cut `idler` or `stranger` off from `mirror`.
>
> Do not admit `tender` by its IP address with `ipBlock`. Pod addresses change when a pod restarts; the label stays.
>
> Do not add a `namespaceSelector` next to the `podSelector` unless it matches only `starfleet-031-010-01-01`. `namespaceSelector: {}` matches every namespace.
