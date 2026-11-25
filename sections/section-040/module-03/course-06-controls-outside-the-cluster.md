# Controls Outside The Cluster

A NetworkPolicy covers the traffic of ordinary pods and nothing more. The node, the cloud account and the physical network each have their own controls. A complete design uses all of them together.

This page is reading only. The playground runs on `kind`, so it has no cloud provider, no instance roles and no security groups. The page describes what each control does and where it applies.

## Limit what the metadata service returns

The first control outside the cluster is the metadata service of the cloud provider. This service answers on the address `169.254.169.254` and gives a machine its settings and, often, the credentials of its role.

On Amazon Web Services (AWS), the settings of the instance decide how the metadata service behaves:

- `HttpTokens` set to `required` turns off the first version of the service and forces the token flow. In the token flow, a client must first ask for a token and then send it with every request.
- `HttpPutResponseHopLimit` sets the time to live of the token response, that is, how many network hops the response can cross. With the value 1, the token cannot cross the extra hop to a container that has its own network namespace. So pods on a bridge network cannot get a token, while processes on the host still can.

Some container platforms raise the hop limit to 2 so that pods work, and that choice opens the path again. The value you need depends on the network plugin, so test it on a sample node.

Other providers have similar switches:

- **Google Cloud** requires the header `Metadata-Flavor: Google` on every request. It offers node pool options that give pods a restricted metadata server instead of the real one.
- **Microsoft Azure** requires the header `Metadata: true`, and it refuses requests that carry a forwarding header.
- **Managed Kubernetes services** offer options to hide the metadata of the node from pods, or to run the node pool without credentials that pods can use.

Names and defaults change over time, so read the current documentation of your provider.

## Give pods their own identity

Limiting the metadata service makes the node role harder to reach. A better fix is that pods do not need the node role at all. Workload identity binds a cloud identity to a Kubernetes ServiceAccount.

It works in two steps. The pod shows its ServiceAccount token to the cloud provider. The provider checks the token and returns short-lived credentials for a role that has only the permissions this workload needs.

The providers use different names for this feature:

- IAM roles for service accounts on Amazon EKS.
- Workload Identity on Google Kubernetes Engine.
- Microsoft Entra Workload ID on Azure Kubernetes Service.

With workload identity in place, you can reduce the node role to what the node itself needs, such as pulling images. A stolen node credential is then worth much less.

## Filter traffic on the node and the network

Identity controls limit what a credential can do. Traffic filters limit who can reach a port in the first place. A firewall on the node or in the cloud network adds the control that a pod policy lacks.

Security groups, network access control lists and node firewall rules decide which machines can reach port 10250 and the control plane ports. Only the control plane and monitoring systems should reach the kubelet port. A host firewall can also drop traffic from the pod network to the node ports. This also covers host network pods, because they use the node's own interface.

Calico can enforce policy at the node itself. A host endpoint object represents a network interface of a node. A `GlobalNetworkPolicy` can select host endpoints and allow or deny traffic to the ports of the node and from its processes.

Host endpoints need care. Once a host endpoint exists, Calico denies traffic on that interface by default. So a rule set that keeps SSH, the kubelet and the API server reachable must exist first, or the node can become unreachable. Calico keeps a short list of failsafe ports open by default, but do not rely on it. The playground does not turn on host endpoints, so you only read about them here.

## Other node settings

The last group of controls is the settings of the node itself. Close what is not needed:

- Turn off the kubelet read-only port.
- Set anonymous authentication to off and authorization to Webhook.
- Rotate the kubelet certificates.
- Keep nodes in private networks without public addresses.
- Patch the operating system of the node and the runtime.
- Restrict who can log in to a node. A person with a shell on the node can read the metadata service, the kubelet credential and the runtime socket directly.

![Diagram: five layers of defence and what each one does: admission control keeps dangerous pods out, NetworkPolicy blocks the paths of allowed pods, provider settings reduce what the metadata service returns, workload identity makes the node role less valuable, and node and network firewalls limit who reaches the node ports](images/defence-layers.svg)

The drawing shows the layers side by side, with the job of each one. Each layer fails in a different way, so a failure in one does not remove the others.

The central idea of this page is layers. Admission control keeps dangerous pods out. NetworkPolicy blocks the paths of the pods that are allowed. Provider settings reduce what the metadata service gives away. Workload identity makes the node role less valuable. Firewalls on the node and the network limit who can reach the node ports at all. No single layer is enough on its own, and the open question for every cluster is which of these layers it still lacks.

## Common pitfalls

> [!WARNING]
> - **Relying on one layer.** Every control above has a known bypass, and the other layers cover it.
> - **Setting the hop limit without testing pods.** A value of 1 can break workloads that need node credentials, and a value of 2 allows pods to reach the service.
> - **Turning on Calico host endpoints without allow rules.** The node can lose its kubelet and SSH connectivity.
> - **Assuming managed clusters are safe by default.** Check the node pool options for the metadata service and the kubelet.
