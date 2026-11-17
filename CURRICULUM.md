# Curriculum Coverage

> Historical design record. Counts and execution claims below describe the original expansion. For current labs, preparation and practical limits, use [LAB-COVERAGE.md](LAB-COVERAGE.md) and [COVERAGE-REVIEW.md](COVERAGE-REVIEW.md).

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

This course has 5 ungraded module playgrounds and 6 draft independent labs. Tasks and solutions are registered around each lab immediately after its teaching reading. Static configuration, shell/Python/YAML, parser, lifecycle and offline grader checks pass. Live execution remains pending because the session cannot access Podman; installed CLI configuration validation is separately blocked by its maintenance lock.

| Module | Labs in teaching order |
| --- | --- |
| 010/01 | Allow One Peer And Deny Another |
| 010/01 | Allow DNS And One Application Dependency |
| 020/01 | Disable API Server Profiling In A Private Node |
| 030/01 | Verify TLS Termination And Server Identity |
| 040/01 | Block A Simulated Metadata Endpoint |
| 050/01 | Verify Signed Artifact Checksums |
