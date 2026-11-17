# Curriculum Coverage

Exam: Certified Kubernetes Security Specialist (CKS). Domain: Cluster Setup (15%).

The [official objectives](https://training.linuxfoundation.org/certification/certified-kubernetes-security-specialist/) were checked on 2026-10-11. Teaching structure is independently authored and does not add official requirements.

| Section | Official objective | Modules |
| --- | --- | --- |
| 010 | Use Network security policies to restrict cluster level access | 1 |
| 020 | Use CIS benchmark to review the security configuration of Kubernetes components (etcd, kubelet, kubedns, kubeapi) | 1 |
| 030 | Properly set up Ingress with TLS | 1 |
| 040 | Protect node metadata and endpoints | 1 |
| 050 | Verify platform binaries before deploying | 1 |

| Section / module | Module | Teaching files |
| --- | --- | --- |
| 010 / 01 | NetworkPolicy Semantics And Verification | Traffic Isolation And Allowed Peers |
| 020 / 01 | Reviewing A Cluster Against A Security Benchmark | Reviewing A Cluster Against A Security Benchmark |
| 030 / 01 | Ingress Routing And TLS Contracts | Matching Ingress Hosts, Paths And Service Backends; PKI Trust And Certificate Verification |
| 040 / 01 | Protecting Node Metadata And Management Endpoints | Protecting Node Metadata And Management Endpoints |
| 050 / 01 | Verifying Release Artifacts Before Deployment | Verifying Release Artifacts Before Deployment |

AUTHORING.yaml records measurable goals and adaptation sources. Every objective retains its section ID. All technical readings remain draft. Question banks are separate from the reading manifest and follow their declared summaries. Playgrounds and draft labs accompany each module; live runtime validation is still pending.

## Hands-On Coverage

This course has 19 ungraded module playgrounds and 86 independent labs. Each lab's task and solution are registered immediately after the reading it practises. Every lab passed `astrona validate` and `astrona test` on kind (arm64 node image) on 2026-11-17.

| Module | Labs in teaching order |
| --- | --- |
| 010/01 | Allow One Peer And Deny Another |
| 010/01 | Allow DNS And One Application Dependency |
| 020/01 | Disable API Server Profiling In A Private Node |
| 030/01 | Verify TLS Termination And Server Identity |
| 040/01 | Block A Simulated Metadata Endpoint |
| 050/01 | Verify Signed Artifact Checksums |
