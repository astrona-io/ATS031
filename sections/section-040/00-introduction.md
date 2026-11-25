# Protect node metadata and endpoints

A pod can have no Kubernetes permissions at all and still be dangerous. From inside the pod, it may reach the cloud metadata service of its node or a management port on the node. Those endpoints can hand out credentials and control that role-based access control (RBAC) never granted.

RBAC only guards the Kubernetes API. It does not see a request that goes straight to an address on the node. In this section, you learn which endpoints on a node carry this kind of authority, which network paths a NetworkPolicy covers and which it does not, and how to restrict and verify what a pod can reach.

## What you will learn

The section moves from finding the risky endpoints to closing them:

- **Protect Node Metadata And Management Endpoints.** The endpoints on a node that carry authority, why a node identity differs from a workload identity, and how to limit a pod with an egress allow-list.
- **Block The Cloud Metadata Endpoint.** The metadata service, an `ipBlock` with `except`, a selective allow for one labelled pod, policy pitfalls and a coverage check.
- **Protect Node Endpoints And The Runtime.** The kubelet ports, node identity and `NodeRestriction`, exposure through the runtime socket and `hostPath`, host network pods, and controls that live outside the cluster.

## How this section works

Each module has its own playground: a private `kind` cluster that runs Kubernetes v1.35 with Calico as the network plugin. Start it from the first page of the module and keep it running while you read, because every page has commands to try.

When a page teaches a skill you can be graded on, a lab comes right after it. A lab gives you a short task in a fresh cluster and checks your result. Each module ends with a summary and a short knowledge check.

## By the end of this section

You will be able to:

- name the endpoints on a node that carry authority: the cloud metadata service, the kubelet API and the container runtime socket;
- explain why the identity of a node differs from the identity of a workload, and why RBAC does not cover a metadata service;
- read the kubelet authentication and authorization settings from a running node, and find pods that mount host paths or use the host network;
- show with requests from two namespaces that a pod can reach a metadata-style endpoint, and restrict it with an egress allow-list;
- explain what a NetworkPolicy does not cover, and name provider-specific protections that add to it;
- block the metadata address for a namespace with an `ipBlock` and an `except` entry, and open it for one labelled pod with a second policy;
- explain why two separate deny-list policies on the same pods cancel each other, and put every exception in one list;
- turn off the kubelet read-only port, restrict pod access to the kubelet ports and read the node authorization settings;
- find pods that mount the container runtime socket or use the host network, remove a socket mount from a workload, and make Pod Security admission reject new host network pods;
- name the controls that live outside the cluster, such as metadata service settings and node identity configuration at a cloud provider.
