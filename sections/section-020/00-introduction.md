# Use CIS benchmark to review the security configuration of Kubernetes components (etcd, kubelet, kubedns, kubeapi)

A cluster can start and run its pods while some of its settings are unsafe. The API server may accept requests it should refuse. The kubelet on a node may answer anyone who asks. A file that holds a private key may be readable by every user on the machine.

The Center for Internet Security (CIS) Kubernetes Benchmark is a published list of recommended settings for these components. A security review compares the real settings of a cluster with that list. The hard part is to read the settings the components really use, not the files that only look relevant. In this section, you learn how to run that review and how to fix what it finds without breaking the cluster.

## What you will learn

The section moves from reading the benchmark to fixing a whole node:

- **Review Kubernetes Components With The CIS Benchmark.** How the benchmark is organised, how to read a check, and how to correct a finding on the API server.
- **Run kube-bench And Read Its Output.** The tool that runs the checks, its targets and versions, and how to judge a result and spot a false finding.
- **Harden The API Server And Control Plane Components.** The API server flags, admission, audit logging and the files of the control plane.
- **Review etcd Security Configuration.** The etcd client and peer TLS flags, the data directory, a direct query with `etcdctl` and encryption at rest.
- **Harden The kubelet And CoreDNS, Then Remediate End To End.** kubelet authentication, authorization and ports, the CoreDNS review and a full remediation.

## How this section works

Each module has its own playground: a virtual machine (VM) that runs a one-node Kubernetes v1.35 cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. Start it from the first page of the module and keep it running while you read. Because the node is a real machine, you read and change the real static pod manifests, etcd files and kubelet settings, as on a node in the exam.

When a page teaches a skill you can be graded on, a lab comes right after it. A lab gives you a short task in a fresh cluster and checks your result. Each module ends with a summary and a short knowledge check.

## By the end of this section

You will be able to:

- explain how the CIS benchmark is organised and which component each part of it covers;
- find the manifests, configuration files and certificates of a kubeadm cluster on a node;
- read a `kube-bench` check (its audit, test and remediation) and run the same audit by hand;
- review the effective kubelet configuration and the permissions of its files;
- correct an API server flag in the static pod manifest, wait for the API server to return, and verify the new value;
- review the etcd TLS flags and data directory permissions, read stored data with `etcdctl`, and turn on encryption at rest for Secrets;
- close anonymous access and open authorization on the kubelet, and fix its ports, certificate rotation and TLS settings;
- review the CoreDNS Deployment, its Corefile and its permissions;
- combine these fixes on one cluster and record the evidence of each change.
