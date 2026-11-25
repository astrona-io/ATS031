# Shrink The Controller Attack Surface

The Ingress controller sits on the edge of the cluster. It takes requests from the internet, and it holds credentials for the Kubernetes API. If an attacker takes over the controller, they get its permissions too.

The attack surface is everything an attacker can reach or use through one component. On this page, you list what a Traefik installation can read, what it exposes and how it runs, and you learn the command that finds each item.

## What the controller can read

Start with the permissions, because they decide what a stolen controller can do inside the cluster. Traefik runs as a ServiceAccount, the identity a pod uses to talk to the Kubernetes API. A ClusterRole gives that ServiceAccount its permissions in every namespace.

Traefik needs to read Secrets to load certificates. In the default installation, this permission is cluster-wide. So a compromised controller can read every Secret in every namespace, not only the TLS Secrets.

A tighter design runs one controller for each team in its own namespace. A Role, which gives permissions in one namespace only, and the namespaces option of the provider then limit the reading to that namespace. The command `kubectl auth can-i` tests a permission for any identity without changing anything.

<!-- astrona:playground:renew -->

```sh
kubectl auth can-i list secrets --all-namespaces --as=system:serviceaccount:ingress-system:traefik
kubectl auth can-i create pods --as=system:serviceaccount:ingress-system:traefik
kubectl get clusterrole traefik -o jsonpath='{range .rules[*]}{.resources}{" "}{.verbs}{"\n"}{end}'
```

The first command answers `yes`, which shows the cluster-wide Secret access. The second answers `no`, so the controller cannot start pods. The third prints the resources and the verbs that the role grants. A controller must never receive more than `get`, `list` and `watch` for these resources.

## What the controller exposes

Permissions are one side of the risk. The other side is the ports the controller opens. Traefik can open more than its two entrypoints, the ports on which it takes client traffic.

With the flag `--api.insecure=true`, the Traefik API and dashboard listen on port 8080 without authentication. Anyone who can reach that port sees every router, service and middleware. The Kubernetes Service decides which ports other pods and the internet can reach. Check the arguments and the Service of this controller:

```sh
kubectl -n ingress-system get deployment traefik -o jsonpath='{.spec.template.spec.containers[0].args}{"\n"}'
kubectl -n ingress-system get service traefik -o jsonpath='{range .spec.ports[*]}{.name}{" "}{.port}{" "}{.targetPort}{"\n"}{end}'
kubectl -n ingress-system get service traefik -o jsonpath='{.spec.type}{"\n"}'
```

The arguments here contain no `--api.insecure` flag, so the API is not enabled. The Service lists only port 80 and port 443. If you ever find `--api.insecure=true` on a controller, treat it as a finding: remove it, or protect the API with a router and authentication.

The Service type matters as well. A Service of type `ClusterIP` is reachable only from inside the cluster, which is the right type for an internal port. Never publish port 8080 through a `LoadBalancer` or `NodePort` Service.

![Diagram: requests from the internet reach the Traefik pod through the entrypoints web and websecure; the pod reads Secrets in all namespaces from the Kubernetes API; and when --api.insecure=true is set, anyone in the cluster network can reach the API and dashboard on port 8080](images/controller-attack-surface.svg)

The drawing shows two paths of risk. Traffic from outside reaches the pod through the entrypoints, and the pod reaches the Kubernetes API with its own permissions. The red dashed path to port 8080 exists only when the insecure API is turned on, which is not the case in this playground.

## What the controller runs as

The last item is the security context of the container: the settings that limit what the process may do on the node. A hardened container drops Linux capabilities, runs as a user that is not root and has a read-only root file system. Read the security settings and the ServiceAccount of the pod:

```sh
kubectl -n ingress-system get deployment traefik -o jsonpath='{.spec.template.spec.containers[0].securityContext}{"\n"}'
kubectl -n ingress-system get deployment traefik -o jsonpath='{.spec.template.spec.serviceAccountName}{"\n"}'
```

An empty result for the first command means the container has no restrictions of its own. Entrypoints above port 1024, like `8000` and `8443` here, do not need extra privileges to bind.

You can now check what the controller may read, which ports it exposes and how its container runs, each with one `kubectl` command. A hardened controller still serves certificates, and every certificate has an end date. The open question is how to replace a certificate before it expires, and how to prove that clients get the new one.

## Common pitfalls

> [!WARNING]
> - **Leaving `--api.insecure=true` on a shared cluster.** Remove it, or protect the API with a router and authentication.
> - **Assuming a TLS Secret is the only Secret the controller can read.** The default role covers every Secret.
> - **Exposing the Service as `LoadBalancer` with all ports.** Publish only port 80 and port 443.
> - **Running the controller as a ServiceAccount with administrator rights.** Give it a role built for its purpose and nothing more.
