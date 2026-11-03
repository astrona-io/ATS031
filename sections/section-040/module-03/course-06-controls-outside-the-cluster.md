---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Controls Outside The Cluster

A NetworkPolicy covers the traffic of ordinary pods and nothing more. The node, the cloud account and the physical network have their own controls, and a complete design uses them together. This part is reading only, because the playground runs on `kind` and has no cloud provider, no instance roles and no security groups. It describes what each control does and where it applies.

## Limit what the metadata service returns

On Amazon Web Services (AWS), the instance settings decide how the metadata service behaves. The setting `HttpTokens` set to `required` turns off the first version of the service and forces the token flow. The setting `HttpPutResponseHopLimit` sets the time to live of the token response. With the value 1 the token cannot cross the extra network hop to a container with its own network namespace, so pods on a bridge network cannot obtain a token, while processes on the host still can. Some container platforms raise the limit to 2 so that pods work, and that choice reopens the path. Which value you need depends on the network plugin, so test it on a sample node.

Other providers have similar switches. Google Cloud requires the header `Metadata-Flavor: Google` on every request and offers node pool options that give pods a restricted metadata server instead of the real one. Microsoft Azure requires the header `Metadata: true` and refuses requests that carry a forwarding header. Managed Kubernetes services offer options to hide the metadata of the node from pods or to run the node pool without credentials that pods can use. Read the current documentation of your provider, since names and defaults change.

## Give pods their own identity

The best fix for the credentials problem is that pods do not need the node role. Workload identity binds a cloud identity to a Kubernetes ServiceAccount. The pod proves its ServiceAccount token to the cloud provider, which returns short-lived credentials for a role that has only the permissions that this workload needs. The names differ: IAM roles for service accounts on Amazon EKS, Workload Identity on Google Kubernetes Engine, and Microsoft Entra Workload ID on Azure Kubernetes Service. With workload identity in place, the node role can be reduced to what the node itself needs, such as pulling images, and a stolen node credential is worth much less.

## Filter traffic on the node and the network

A firewall on the node or in the cloud network adds the control that a pod policy lacks. Security groups, network access control lists and node firewall rules decide which machines can reach port 10250 and the control plane ports. Only the control plane and monitoring systems should reach the kubelet port. A host firewall can also drop traffic from the pod network to the node ports, which applies to host network pods as well, since they use the node's own interface.

Calico can enforce policy at the node itself. A host endpoint object represents the network interface of a node, and a `GlobalNetworkPolicy` can select host endpoints and allow or deny traffic to the node's ports and from its processes. Policy on host endpoints is deny by default for the interface once a host endpoint exists, so a rule set that keeps SSH, the kubelet and the API server reachable must exist first, or the node can become unreachable. Calico keeps a short list of failsafe ports open by default, but do not rely on it. The playground does not enable host endpoints, so you only read about them here.

## Other node settings

Close what is not needed. Turn off the kubelet read-only port, set anonymous authentication to off and authorization to Webhook, and rotate the kubelet certificates. Keep nodes in private networks without public addresses. Patch the node operating system and the runtime. Restrict who can log in to a node, because a person with a shell on the node can read the metadata service, the kubelet credential and the runtime socket directly.

The central idea is layers. Admission control keeps dangerous pods out. NetworkPolicy blocks the paths of pods that are allowed. Provider settings reduce what the metadata service gives away. Workload identity makes the node role less valuable. Each layer fails differently, so a failure in one does not remove the others.

## Common pitfalls

> [!WARNING]
> - **Relying on one layer.** Every control above has a known bypass, and the others cover it.
> - **Setting the hop limit without testing pods.** A value of 1 can break workloads that need node credentials, and a value of 2 allows pods to reach the service.
> - **Enabling Calico host endpoints without allow rules.** The node can lose its kubelet and SSH connectivity.
> - **Assuming managed clusters are safe by default.** Check the node pool options for metadata and the kubelet.
