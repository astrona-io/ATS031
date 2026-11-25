# Set Up Ingress With TLS

Many web applications run inside one Kubernetes cluster, but users outside the cluster must reach them through one address. An Ingress is the Kubernetes object that solves this. It holds rules that route HTTP and HTTPS requests from outside the cluster to Services inside it, based on the host name and the URL path of each request.

Without encryption, every request and response crosses the network in clear text. The client also has no way to know whether it talks to the right server. Transport Layer Security (TLS) is the protocol that fixes both problems. It encrypts the connection, and it lets the client check the identity of the server with a certificate.

An Ingress object does nothing by itself. A separate program, the Ingress controller, watches Ingress objects and does the routing. In this module the controller is Traefik. The controller also terminates TLS. That means it holds the certificate and the private key, which it reads from a Kubernetes Secret, and it forwards the decrypted request to the Service.

## What you will learn

After this module, you can:

- explain the roles of the Ingress object, the IngressClass and the Ingress controller;
- write Ingress rules with a host, a path, a `pathType` and a backend Service port;
- create a `kubernetes.io/tls` Secret from a certificate and a key, and check that the two match;
- configure `spec.tls` in an Ingress and explain which certificate a client receives for a given host name;
- test with `curl` and `openssl s_client` that the certificate is trusted for the matching name and rejected for another name.

## How the module is laid out

You start with **Ingress Routing: Controller, Class, Host And Path**, which explains which component does what and routes a first request without TLS. **Certificates And The TLS Secret** then shows what a certificate contains, what a client checks, and how to store a certificate and key in a Secret. **Configure An Ingress With TLS And Verify It** attaches the Secret to an Ingress and tests it with certificate checks turned on. **Several Hosts, Server Name Selection And Troubleshooting** closes the module with many host names on one controller and a method to find the cause of a failure.

A lab follows each part, so you can practise the skill right away.

## Before you start

You should know the Kubernetes basics: Deployments, pods, Services, Secrets and `kubectl`. You also need `curl` and `openssl` on your own machine.

## Your playground

Your playground is a `kind` cluster that runs Kubernetes v1.35 and the Traefik Ingress controller. No Ingress exists yet. The cluster already runs these objects:

| Namespace | Object | What it is |
| --- | --- | --- |
| `starfleet` | `probe` Deployment, two pods, labels `app: probe` and `release: probe` | A small web server that listens on pod port 8080; its code comes from the `probe-code` ConfigMap |
| `starfleet` | `probe` Service | Port 80, forwards to port 8080 of the `probe` pods |
| `starfleet` | `probe-tls` Secret | A self-signed certificate and key for the host name `probe.local`, valid for one day |
| `starfleet` | `shuttle` pod, label `app: shuttle` | A client pod with `wget` |
| `outpost` | `drifter` pod, label `app: drifter` | A client pod with `wget`, in another namespace |
| `ingress-system` | `traefik` Deployment, one pod | The Ingress controller, with the entrypoints `web` (pod port 8000) and `websecure` (pod port 8443) |
| `ingress-system` | `traefik` Service | Port 80 for HTTP (`web`) and port 443 for HTTPS (`websecure`) |
| `ingress-system` | `traefik` ServiceAccount | The identity of the controller; the `ckad-traefik` ClusterRole lets it read Ingresses, Services, EndpointSlices and Secrets |
| (cluster-wide) | `traefik` IngressClass | Names the controller `traefik.io/ingress-controller`, so Ingress objects can select it |

`kubectl` already points at the playground cluster. Start your playground now and keep it running while you read:

<!-- astrona:playground -->
