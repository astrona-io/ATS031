---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Egress To The API Server And Other Dependencies

Some pods call the Kubernetes API server, for example controllers, operators and monitoring agents. Some call services outside the cluster. Under an egress baseline both need a rule, and neither can be written with a label selector. This part shows how to find the address that a policy must allow for the API server, reads the rule that the playground already uses, and explains the `ipBlock` form for external services.

## The kubernetes Service and its endpoint

Every cluster has a Service named `kubernetes` in the `default` namespace. Its cluster IP address is the address that pods get in the environment variable `KUBERNETES_SERVICE_HOST`. The Service forwards to the real address of the API server, which is listed in an EndpointSlice, the object that stores the addresses behind a Service.

<!-- astrona:playground:renew -->

```sh
kubectl get service kubernetes
kubectl get endpointslice -l kubernetes.io/service-name=kubernetes
kubectl get endpointslice -l kubernetes.io/service-name=kubernetes -o jsonpath='{.items[0].endpoints[0].addresses[0]}{"\n"}{.items[0].ports[0].port}{"\n"}'
```

The first command shows the Service cluster IP address and port 443. The second shows the EndpointSlice. The third prints the endpoint address and its port. In a `kind` cluster this is normally the address of the control plane node container, and the port is normally 6443.

## Which address to allow

The node rewrites the Service address to the endpoint address before the plugin applies the policy, so Calico matches the endpoint address and port. A rule that allows only the Service address `10.x.x.x:443` therefore may not match. Allow the endpoint address with its port. Plugins differ here, and managed clusters often place the API server behind a load balancer address, so verify the behaviour in the cluster you use by testing the call.

The API server is not a pod, so you cannot select it by label. You use an `ipBlock` with the address and a `/32` prefix, which selects exactly one address, together with the port.

## Read the rule that exists

The playground already allows `scout` to reach the API server. Read the policy that does it, and run the script again:

```sh
kubectl -n starfleet get networkpolicy scout-egress -o yaml
kubectl -n starfleet exec scout -- python /app/check.py
```

The policy lists one `ipBlock` with the control plane address and TCP port 6443 under `egress`. The script step `api` must show `ok`, which means the call to the API server with the ServiceAccount token worked and that this rule is correct. The ServiceAccount also needs permission to list pods in `starfleet`, and role-based access control is a separate layer: NetworkPolicy lets the connection through, and RBAC decides what the request may do.

## Why only one pod gets the rule

The rule selects the `scout` pod, not the namespace. A pod that holds a ServiceAccount token and can reach the API server is a target. Giving the API server rule to a single workload keeps the other pods unable to reach it, even if one of them is compromised and holds a token.

## External services

A service outside the cluster has an address range and no labels. The rule uses `ipBlock` for it. A fragment inside an `egress` rule looks like this:

```yaml
  - to:
    - ipBlock:
        cidr: 203.0.113.0/24
        except:
        - 203.0.113.99/32
    ports:
    - protocol: TCP
      port: 443
```

The fragment allows HTTPS to the range and excludes one address. The range `203.0.113.0/24` belongs to a documentation address block and serves here only as an example. If the external service is reached by a DNS name that points to changing addresses, a plain NetworkPolicy cannot follow the name, because it has no field for names. Teams use an egress gateway, a proxy with a fixed address, or a plugin-specific policy for this case.

You can now find and allow the API server address and write an external CIDR rule. The next part covers traffic that policies never see.

## Common pitfalls

> [!WARNING]
> - **Allowing the Service cluster IP address.** The plugin may match the endpoint address after translation.
> - **Giving the API rule to the whole namespace.** Select only the pods that need the API.
> - **Reading NetworkPolicy as authorization.** It opens the network path; RBAC still decides what the request may do.
> - **Expecting a rule for a DNS name.** The API has no field for names, only addresses.
